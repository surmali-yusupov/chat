from fastapi import HTTPException, status

CredentialsError = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={'WWW-Authenticate': 'Bearer'},
)

UserNotFound = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail='User With this username not found'
)

IncorrectPassword = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='Incorrect password'
)

InvalidData = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail='Invalid data provided',
)

notAuthenticated = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='Not authenticated',
    headers={'WWW-Authenticate': 'Bearer'},
)

inactiveUser = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail='Inactive user',
)
