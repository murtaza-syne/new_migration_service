
class BaseExceptionError(Exception):
    def __init__(self, message='please check params',error_code = 400,e = None):
        super().__init__(message,error_code,e)

