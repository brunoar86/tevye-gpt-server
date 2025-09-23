import structlog

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from tevye_gpt_server.src.interfaces.auth import RegistrationForm
from tevye_gpt_server.src.controllers.auth_controller import auth

router = APIRouter()
log = structlog.get_logger(__name__='register route')



