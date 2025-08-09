import structlog
import uvicorn

from tevye_gpt_server.src.main import app

log = structlog.get_logger(__name__='main module')


def start():
    log.info("Starting Tevye GPT server")
    log.info("Using FastAPI version", version=app.version)
    log.info("Listening on port 8080")
    uvicorn.run(app, host='0.0.0.0', port='8080', reload=True, debug=False)
    log.info("Tevye GPT server started")


if __name__ == '__main__':
    start()
