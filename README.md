# Email-Buffer-Save-State
A custom buffering email loggger class and corresponding save state class for python scripts.

## BufferingSMTPHandler Class
The **BufferingSMTPHandler** class is a custom logging handler that extends the **BufferingHandler** class. It is designed to buffer log records and send them as a single email when the buffer is flushed. This class is particularly useful for sending error alerts via email in a batch, rather than sending an email for each individual log record.

### Attributes:
- **email_dict** (*dict*): A dictionary containing email settings such as the sender address, recipient addresses, SMTP host, and port.
- **state** (*StateJar*): An instance of the StateJar class used to save and load the state of the buffer.
- **buffer** (*list*): A list to store log records until they are flushed.
- **capacity** (*int*): The maximum size of the buffer before it is flushed. In this case, it is set to 5 MB.
### Methods:
- **__init__**(*self, email_settings, paths*): Initializes the BufferingSMTPHandler with email settings and paths.

  - **email_settings** (*dict*): A dictionary containing email settings to use.
  - **paths** (*str*): The path to the save file for the state jar.
- **flush**(*self, force=False, custom_alerts=None*): Flushes the buffer if it exceeds the threshold or if forced.

  - **force** (*bool*): If True, forces the buffer to flush regardless of its size.
  - **custom_alerts** (*list*): A list of custom alert messages to include in the email body.
- **save**(*self*): Saves the buffer for later use (if it isn't full yet or can't be emptied).

- **shouldFlush**(*self, record*): Returns False to stop automatic flushing by the buffering handler by default (flushing is done manually).

## StateJar Class
The **StateJar** class is a custom class designed to load and save the state of outcomes and data using JSON. It is particularly useful for persisting the state of log records between script runs, ensuring that important information is not lost if the script is interrupted or encounters an error.

### Attributes:
- **filepath** (str): The path to the JSON file where the state will be saved.
- **buffer** (list): A list to store log records.
### Methods:
- **__init__**(self, filepath: str) -> None: Initializes the StateJar with a file path.
  - **filepath** (str): The path to the JSON file where the state will be saved.
- **save**(self) -> None: Saves the current state to a JSON file.
- **to_dict**(self) -> dict: Converts the StateJar object to a dictionary, ensuring all log records are JSON serializable.
  - *Returns*: A dictionary representation of the StateJar object.
- **serialize_record**(record: logging.LogRecord) -> dict: Serializes a log record to a JSON-serializable dictionary.
  - **record** (logging.LogRecord): The log record to serialize.
  - *Returns*: A dictionary representation of the log record.
- **load**(cls, filepath: str) -> "StateJar": Loads the StateJar object from a JSON file.
  - **filepath** (str): The path to the JSON file.
  - *Returns*: The loaded StateJar object.
- **deserialize_record**(record: dict) -> logging.LogRecord: Deserializes a dictionary to a log record.
  - **record** (dict): The dictionary representation of the log record.
  - *Returns*: The deserialized log record.
