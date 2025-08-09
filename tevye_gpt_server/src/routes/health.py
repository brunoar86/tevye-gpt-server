import structlog

from fastapi import APIRouter

router = APIRouter()
log = structlog.get_logger(__name__='health routes')


@router.get('/live', tags=['Health'])
def live():
    '''
    Route to check liveness
    '''
    log.info("Liveness check called")
    return {'message': 'Tevye OpenAI API is live!'}


@router.get('/ready', tags=['Health'])
def ready():
    '''
    Route to check readiness
    '''
    log.info("Readiness check called")
    return {'message': 'Tevye OpenAI API is ready!'}
