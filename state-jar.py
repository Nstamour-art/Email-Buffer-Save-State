import json
import logging

class StateJar:
    """
    A custom save class to load and save the state of the outcomes and data using JSON as required
    """

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.buffer = []

    def save(self) -> None:
        with open(self.filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=4)

    def to_dict(self) -> dict:
        """
        Convert the StateJar object to a dictionary, ensuring all log records are JSON serializable.
        """
        return {
            "filepath": self.filepath,
            "buffer": [self.serialize_record(record) for record in self.buffer],
        }

    @staticmethod
    def serialize_record(record: logging.LogRecord) -> dict:
        """
        Serialize a log record to a JSON-serializable dictionary.
        """
        return {
            "name": record.name,
            "levelname": record.levelname,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "asctime": record.asctime if hasattr(record, "asctime") else None,
        }

    @classmethod
    def load(cls, filepath: str) -> "StateJar":
        """
        Load the StateJar object from a JSON file.
        Args:
            filepath (str): Path to the JSON file.

        Returns:
            StateJar: Loaded StateJar object.
        """
        if os.path.isfile(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                obj = cls(filepath)
                obj.__dict__.update(data)
                obj.buffer = [cls.deserialize_record(record) for record in obj.buffer]
                return obj
        else:
            obj = cls(filepath)
            obj.save()  # Create the file if it doesn't exist
            return obj

    @staticmethod
    def deserialize_record(record: dict) -> logging.LogRecord:
        """
        Deserialize a dictionary to a log record.
        """
        log_record = logging.LogRecord(
            name=record["name"],
            level=logging.getLevelName(record["levelname"]),
            pathname=record["pathname"],
            lineno=record["lineno"],
            msg=record["message"],
            args=(),
            exc_info=None,
        )
        log_record.asctime = record["asctime"]
        return log_record
