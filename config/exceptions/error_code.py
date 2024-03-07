import enum 
class BussinessErrorCode(enum.Enum):
    EMAIL_NOT_EXISTED = "LGN_001"
    EMAIL_EXISTED = "USR_017"
    PHONE_EXISTED = "USR_018"
    USER_NOT_EXISTS = "USR_019"
    PASSWORD_MISMATCH = "USR_022"
    VIDEO_EMPTY = "VID_000"
    LOCALE_NOT_EXISTED = "LCL_001"
    PROCESS_STATUS_INVALID = "VID_001"
    DELETE_VIDEO_FAILED = "VID_002"
    SUBTITLE_NOT_EXISTED = "SUB_001"
    LABEL_NOT_FOUND = "LBL_001"
    WRONG_PASSWORD = "LGN_002"
    
class InternalErrorCode(enum.Enum):
    UPLOAD_VIDEO_ERROR = "SYS_001"
    CONVERT_VIDEO_ERROR = "SYS_002"