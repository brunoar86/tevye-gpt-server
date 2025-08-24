from pydantic import BaseModel


class RegistrationForm(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str
