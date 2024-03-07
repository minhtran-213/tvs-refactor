from config.exceptions.error_code import BussinessErrorCode, InternalErrorCode

class BusinessErrorException(Exception):
    status_code: BussinessErrorCode
    message: str

    def __init__(self, status_code: BussinessErrorCode, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
    
    
class InternalErrorException(Exception):
    status_code: InternalErrorCode
    message: str

    def __init__(self, status_code: InternalErrorCode, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.message = message