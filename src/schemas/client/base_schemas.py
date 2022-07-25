from pydantic import BaseModel, EmailStr, Field


class ClientBaseSchema(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=9, max_length=15, regex=r'^([\d]+)$')


class ClientPatchSchema(ClientBaseSchema):
    email: EmailStr | None
    phone: str | None = Field(None, min_length=9, max_length=15, regex=r'^([\d]+)$')


class ClientDeleteSchema(ClientBaseSchema):
    pass


class ClientPostSchema(ClientBaseSchema):
    pass


class ClientGetSchema(ClientBaseSchema):
    id: int

    class Config:
        orm_mode = True
