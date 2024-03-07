from fastapi import Request, status
from fastapi.responses import JSONResponse
from models.responses import GenericResponse
from config import utils
from config.exceptions.custom_exceptions import BusinessErrorException, InternalErrorException
import os
import json

def handle_exception(request: Request, exception: BusinessErrorException | InternalErrorException):
    error_response = __get_error_response(exception.status_code.value)
    business_error_response = GenericResponse.generate_generic_response(body=error_response, status_code="FAILED")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=business_error_response
    )

def __get_error_response(error_code: str):
    root_path = utils.get_root_path()
    status_code_path = os.path.join(root_path, 'resources', 'config', 'statusCode.json')
    with open(status_code_path, 'r') as file:
        status_json = json.load(file)
    return {
        'error_field': status_json['errorCodes'][error_code]['errorField'],
        'message': status_json['errorCodes'][error_code]['message']
    }

if __name__ == '__main__':
    response = __get_error_response('USR_003')
    print(response)