from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials
from secrets import compare_digest

from app.config import settings

security = HTTPBasic()

def verify_user(
    credentials: HTTPBasicCredentials = Depends(
        security
    )
):

    username_correct = compare_digest(
        credentials.username,
        settings.API_USERNAME
    )

    password_correct = compare_digest(
        credentials.password,
        settings.API_PASSWORD
    )

    if not (
        username_correct
        and
        password_correct
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={
                "WWW-Authenticate": "Basic"
            },
        )

    return credentials.username