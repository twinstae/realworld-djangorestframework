from typing import Union, Tuple

import jwt
from jwt import PyJWTError

from django.conf import settings
from rest_framework import authentication, exceptions

from .models import JwtUser
from ...strings import COULD_NOT_DECODE_TOKEN, NO_USER_FOUND, USER_HAS_BEEN_DEACTIVATED


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Token'

    def authenticate(self, request) -> Union[None, Tuple[JwtUser, str]]:
        request.user = None

        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) is not 2:
            return None

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            return None

        return self._authenticate_credentials(token)

    @staticmethod
    def _authenticate_credentials(token) -> Tuple[JwtUser, str]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except PyJWTError:
            raise exceptions.AuthenticationFailed(COULD_NOT_DECODE_TOKEN)

        try:
            user = JwtUser.objects.get(pk=payload['id'])
        except JwtUser.DoesNotExist:
            raise exceptions.AuthenticationFailed(NO_USER_FOUND)

        if not user.is_active:
            raise exceptions.AuthenticationFailed(USER_HAS_BEEN_DEACTIVATED)

        return user, token
