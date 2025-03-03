# Email-Buffer-Save-State
An email buffer class and corresponding save state class for python scripts

## BufferingSMTPHandler Class
The **BufferingSMTPHandler** class is a custom logging handler that extends the **BufferingHandler** class. It is designed to buffer log records and send them as a single email when the buffer is flushed. This class is particularly useful for sending error alerts via email in a batch, rather than sending an email for each individual log record.

### Attributes:
- **email_dict**: A dictionary containing email settings such as the sender address, recipient addresses, SMTP host, and port.
- **state**: An instance of the StateJar class used to save and load the state of the buffer.
- **buffer**: A list to store log records until they are flushed.
- **capacity**: The maximum size of the buffer before it is flushed. In this case, it is set to 5 MB.
### Methods:
- **__init__**(*self, email_settings, paths*): Initializes the BufferingSMTPHandler with email settings and paths.

-- **email_settings** (*dict*): A dictionary containing email settings to use.
-- **paths** (*str*): The path to the save file for the state jar.
- **flush**(*self, force=False, custom_alerts=None*): Flushes the buffer if it exceeds the threshold or if forced.

-- **force** (*bool*): If True, forces the buffer to flush regardless of its size.
-- **custom_alerts** (*list*): A list of custom alert messages to include in the email body.
- **save**(*self*): Saves the buffer for later use (if it isn't full yet or can't be emptied).

- **shouldFlush**(*self, record*): Returns False to stop automatic flushing by the buffering handler by default (flushing is done manually).
