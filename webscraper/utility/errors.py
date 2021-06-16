import sys, logging, os
from werkzeug.exceptions import HTTPException


def log_error(exception):
    exception_type, exception_object, exception_traceback = sys.exc_info()
    filename = exception_traceback.tb_frame.f_code.co_filename
    logging.error(
        f"{exception_type.__name__} at line {exception_traceback.tb_lineno} in {filename}: {exception}"
    )


def handle_exception(e):
    response = e.get_response()
    log_error(e)


class NotFoundException(HTTPException):
    code = 404
    description = "Resource cannot be found."


class BadRequestException(HTTPException):
    code = 400
    description = "Bad request."


class AlreadyExistsException(HTTPException):
    code = 400
    description = "Item already exists."


class MissingRequiredFieldException(HTTPException):
    code = 400
    description = "A required field is missing."


class IncorrectInfoException(HTTPException):
    code = 401
    description = "Incorrect information given."


class InternalServerException(HTTPException):
    code = 500
    description = "Internal server error."
