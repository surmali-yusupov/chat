from fastapi.openapi.models import SecurityBase as SecurityBaseModel, SecuritySchemeType as sst
from fastapi.security.utils import get_authorization_scheme_param
from fastapi import Request, status, HTTPException
from fastapi.security.base import SecurityBase
from typing import Optional


class BasicAuth(SecurityBase):
    def __init__(self, scheme_name: str = None, raise_exception: bool = True):
        self.scheme_name = scheme_name or self.__class__.__name__
        self.raise_exception = raise_exception
        self.model = SecurityBaseModel(type=sst.http)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get('Authorization')
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != 'basic':
            if self.raise_exception:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authenticated')
            else:
                return None
        return param


basic_auth = BasicAuth()
