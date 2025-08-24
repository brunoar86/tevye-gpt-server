import structlog

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from tevye_gpt_server.src.interfaces import RegistrationForm

router = APIRouter()
log = structlog.get_logger(__name__='register route')


@router.post('auth/register', tags=['User'])
def register(registration_form: RegistrationForm,
             request: Request, response: Response):
    '''
    Route to handle user registration
    '''
    log.info("Register request received", method=request.method,
             url=request.url)
    try:
        data = request.json()
        log.info("Register request data", data=data)
        # Here you would process the registration request and return a response
        return JSONResponse(content={'message': 'User registration placeholder'})
    except HTTPException as e:
        log.error("HTTP exception occurred", detail=str(e.detail))
        raise e
    except Exception as e:
        log.error("Unexpected error occurred", error=str(e))
        return JSONResponse(status_code=500, content={'message': 'Internal Server Error'})    # noqa: E501