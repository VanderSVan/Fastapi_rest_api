from pydantic import BaseModel as BaseScheme


class TokenData(BaseScheme):
    username: str | None = None
