import structlog

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from tevye_gpt_server.src.interfaces.auth import RegistrationForm
from tevye_gpt_server.src.controllers.auth_controller import auth

router = APIRouter()
log = structlog.get_logger(__name__='register route')


@router.post('/auth/register', tags=['User'])
def register(registration_form: RegistrationForm,
             request: Request, response: Response):
    '''
    Route to handle user registration
    '''
    log.info("Register request received", method=request.method,
             url=request.url)
    try:
        auth.register_user(registration_form)
        log.info("User registered successfully",
                 username=registration_form.username,
                 email=registration_form.email)
        return JSONResponse(content={'message': '{} registered on Tevye GPT!'.format(registration_form.username)})    # noqa: E501
    except HTTPException as e:
        log.error("HTTP exception occurred", detail=str(e.detail))
        raise e
    except Exception as e:
        log.error("Unexpected error occurred", error=str(e))
        return JSONResponse(status_code=500, content={'message': str(e)})    # noqa: E501
