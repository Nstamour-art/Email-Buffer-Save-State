import logging
from datetime import datetime
from logging.handlers import BufferingHandler
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class BufferingSMTPHandler(BufferingHandler):
    """
    Custom SMTPHandler that sends out one single email for every flush
    """

    def __init__(self, email_settings, paths):
        """
        Initialize the BufferingSMTPHandler with email settings and paths.
        Args:
            email_settings (dict): dict containing email settings to use
            paths (str): path to the save file for the state jar
        """
        BufferingHandler.__init__(self, capacity=5 * 1024 * 1024)  # 5 MB capacity
        self.state = StateJar(paths)
        self.buffer = self.state.buffer
        self.email_dict = email_settings
        smtp_formatter = logging.Formatter(
            "%(asctime)s - %(filename)s - %(funcName)s - %(lineno)d - [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.setFormatter(smtp_formatter)

    def flush(self, force=False, custom_alerts=None):
        """
        Flush if we exceed threshold or if forced; otherwise save the buffer
        :param force: Force the flush
        :param custom_alerts: Custom alerts to include in the email body
        :return: None
        """
        notify(lvl="debug", msg="Entering flush method")
        if not self.buffer:
            self.outcome = Outcome(None, "Buffer was empty")
            notify(lvl="debug", msg="Buffer was empty")
            return

        if len(self.buffer) < self.capacity and not force:
            self.outcome = Outcome(None, "Buffer does not have enough messages")
            notify(lvl="debug", msg="Buffer does not have enough messages")
            self.save()
            return

        body = str()

        body += f"Error Alert - {datetime.today().strftime("%m-%d-%Y")} - Specific Error Messages:\r\n{'-'*40}\r\n"

        if custom_alerts:
            body += "\r\n".join(custom_alerts) + "\r\n"

        for record in self.buffer:
            record.asctime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            record.levelname = record.levelname.upper()
            record.filename = os.path.basename(record.pathname)
            record.funcName = record.funcName
            record.lineno = record.lineno
            body += (
                f"{record.asctime} - {record.caller_filename} - {record.caller_funcName} - {record.caller_lineno} - [{record.levelname}] - {record.getMessage()}"
                + "\r\n"
            )

        msg = MIMEMultipart()
        msg["From"] = self.email_dict["fromaddr"]
        msg["To"] = ", ".join(self.email_dict["toaddrs"])
        msg["Subject"] = self.email_dict["subject"]

        # attach the log messages

        msg.attach(MIMEText(body.encode("utf-8"), _charset="utf-8"))

        # attach the log file
        log_file_path = os.path.join(LOGGING_PATH, LOG_FILE_NAME)

        try:
            with open(log_file_path, "rb") as log_file:
                part = MIMEApplication(log_file.read(), Name=LOG_FILE_NAME)
                part["Content-Disposition"] = f'attachment; filename="{LOG_FILE_NAME}"'
                msg.attach(part)
        except FileNotFoundError as e:
            notify(msg=f"Error: Could not find the log file - {e}", lvl="debug")
            raise SystemExit(1)

        try:
            with smtplib.SMTP(
                self.email_dict["host"], self.email_dict["port"], timeout=10
            ) as smtp:
                smtp.ehlo()
                if self.email_dict.get("starttls"):
                    smtp.starttls()
                    smtp.login(self.email_dict["fromaddr"], self.email_dict["password"])
                smtp.sendmail(
                    self.email_dict["fromaddr"],
                    self.email_dict["toaddrs"],
                    msg.as_string(),
                )
                self.outcome = Outcome(True, "Successfully sent e-mail")
                notify(msg="Successfully sent e-mail", lvl="debug")
        except (
            smtplib.SMTPException,
            socket.timeout,
            ConnectionRefusedError,
            socket.gaierror,
        ) as exception_error:
            self.outcome = Outcome(False, str(exception_error))
            notify(msg=f"Failed to send e-mail: {exception_error}", lvl="debug")
            self.save()
            return

        self.buffer = []
        self.save()
        notify(msg="Buffer flushed and saved", lvl="debug")

    def save(self):
        """
        Save the buffer for some other time (it either isn't full yet or we can't empty it)
        """
        self.state.buffer = self.buffer
        self.state.save()
        self.buffer = []

    def shouldFlush(self, record):
        """Returns false to stop automatic flushing (we flush on close)"""
        return False
