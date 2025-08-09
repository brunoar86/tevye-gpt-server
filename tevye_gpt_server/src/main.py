from fastapi import FastAPI

from tevye_gpt_server.src.routes import health
from tevye_gpt_server.src.routes import conversation

app = FastAPI(title='Tevye GPT Server', docs_url='/swagger',
              openapi_url='/openapi.json', version='0.1.0')

app.include_router(health.router)
app.include_router(conversation.router)
