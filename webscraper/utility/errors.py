from werkzeug.exceptions import HTTPException


class UserNotFoundException(HTTPException):
    code = 404
    description = "User cannot be found."


class InsufficientPermissionsException(HTTPException):
    code = 403
    description = "User does not have the correct permissions."


class BadRequestException(HTTPException):
    code = 400
    description = "Bad request."


class AlreadyExistsException(HTTPException):
    code = 400
    description = "Item already exists."


class MissingRequiredFieldException(HTTPException):
    code = 400
    description = "A required field is missing."


class ValueError(HTTPException):
    code = 400
    description = "A required value is missing or incorrect."


class IncorrectInfoException(HTTPException):
    code = 401
    description = "Incorrect information given."


class InternalServerException(HTTPException):
    code = 500
    description = "Internal server error."
