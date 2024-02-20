import enum


class ProcessStatus(enum.Enum):
    PROCESSING = "PROCESSING",
    DONE = "DONE",
    FAILED = "FAILED",
    DUPLICATED = "DUPLICATED",
    UPLOADING = "UPLOADING"


class VideoOptionRequest(enum.Enum):
    AUDIO = "AUDIO",
    SUB = "SUB"
