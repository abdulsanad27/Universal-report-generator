from abc import ABC, abstractmethod

from models.report import Report


class BaseParser(ABC):
    """
    Base class for every parser.

    Every parser MUST inherit this class.
    """

    @abstractmethod
    def parse(self, file_bytes: bytes) -> Report:
        """
        Parse uploaded file and return Report object.
        """
        pass

    def decode_file(self, file_bytes: bytes) -> str:
        """
        Decode bytes safely.
        """

        encodings = [
            "utf-8",
            "utf-16",
            "latin-1"
        ]

        for encoding in encodings:

            try:
                return file_bytes.decode(encoding)

            except UnicodeDecodeError:
                continue

        raise Exception("Unable to decode uploaded file.")