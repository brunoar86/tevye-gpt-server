from pydantic import BaseModel


class GatewayRequest(BaseModel):
    service: str
    payload: dict
