from rest_framework.exceptions import APIException

class CustomAPIException(APIException):
    status_code = 400
    default_detail = 'A server error occurred.'
    default_code = 'error'

    def __init__(self, detail=None, status_code=None):
        if detail is not None:
            self.detail = {'error': detail}
        if status_code is not None:
            self.status_code = status_code
