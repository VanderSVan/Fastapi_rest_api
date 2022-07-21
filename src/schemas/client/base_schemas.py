from pydantic import BaseModel, EmailStr, Field


class ClientBaseSchema(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=9, max_length=15, regex=r'^([\d]+)$')


class ClientPutSchema(ClientBaseSchema):
    pass


class ClientDeleteSchema(ClientBaseSchema):
    pass


class ClientPostSchema(ClientBaseSchema):
    pass


class ClientGetSchema(ClientBaseSchema):
    id: int

    class Config:
        orm_mode = True
