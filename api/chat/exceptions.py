from fastapi import HTTPException, status

NotEnoughRights = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='Permission Denied',
)
