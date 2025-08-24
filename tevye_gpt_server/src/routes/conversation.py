import structlog

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from tevye_gpt_server.src.modules.conversation import chat

router = APIRouter()
log = structlog.get_logger(__name__='index routes')


@router.post('/chat', tags=['Chat'])
async def request_conversation(request: Request, response: Response):
    '''
    Route to handle chat requests
    '''
    log.info("Chat request received", method=request.method, url=request.url)
    try:
        data = request.json()
        log.info("Chat request data", data=data)
        await chat.request(data)
        return JSONResponse(content={'message': 'Chat response placeholder'})
    except HTTPException as e:
        log.error("HTTP exception occurred", detail=str(e.detail))
        raise e
    except Exception as e:
        log.error("Unexpected error occurred", error=str(e))
        return JSONResponse(status_code=500, content={'message': 'Internal Server Error'})    # noqa: E501
