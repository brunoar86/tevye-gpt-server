import structlog

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from tevye_gpt_server.src.interfaces.gateway import GatewayRequest
from tevye_gpt_server.src.controllers.service_controller import service
from tevye_gpt_server.src.utils.app_security import verify_jwt_from_request


router = APIRouter(prefix='/gateway', tags=['gateway'])
log = structlog.get_logger(__name__='index routes')


@router.post('/services', status_code=200)
async def request_service(data: GatewayRequest, request: Request,
                          response: Response):
    '''
    Route to handle requests to tevye ecosystem services.
    '''
    log.info("Request received", method=request.method, url=request.url)
    claims = verify_jwt_from_request(request)
    log.info("JWT verified", sub=claims.get('sub'), scopes=claims.get('scope'))

    try:
        log.info("Request data", service=data.service)
        service_response = await service.request(data)
        return JSONResponse(status_code=200, content=service_response)
    except HTTPException as e:
        log.error("HTTP exception occurred", detail=str(e.detail))
        raise e
    except Exception as e:
        log.error("Unexpected error occurred", error=str(e))
        return JSONResponse(status_code=500, content={'message': 'Internal Server Error'})    # noqa: E501
