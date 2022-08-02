from datetime import datetime as dt
from datetime import timedelta as td

from jose import jwt, JWTError
from fastapi import status

from src.config import Settings
from src.utils.exceptions import JSONException


class JWT:
    @classmethod
    def create_access_token(cls, data: dict, expires_delta: td | None = td(minutes=15)) -> str:
        data_to_encode = data.copy()
        expire = dt.utcnow() + expires_delta
        data_to_encode.update({"exp": expire})

        return jwt.encode(data_to_encode,
                          Settings.SECRET_KEY,
                          algorithm=Settings.ALGORITHM
                          )

    @classmethod
    def extract_payload_from_token(cls, token: str) -> dict:
        try:
            return jwt.decode(token,
                              Settings.SECRET_KEY,
                              algorithms=[Settings.ALGORITHM]
                              )
        except JWTError:
            raise JSONException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Failed to verify credentials. Try logging in again.",
                headers={"WWW-Authenticate": "Bearer"}
            )
