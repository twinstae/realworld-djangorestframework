from rest_framework.exceptions import APIException

from realworld.strings import PROFILE_DOES_NOT_EXIST


class ProfileDoesNotExist(APIException):
    status_code = 400
    default_detail = PROFILE_DOES_NOT_EXIST
