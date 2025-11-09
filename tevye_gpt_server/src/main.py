from fastapi import FastAPI

from tevye_gpt_server.src.routes import health
from tevye_gpt_server.src.routes import gateway
from tevye_gpt_server.src.routes import auth

app = FastAPI(title='Tevye GPT Server', docs_url='/swagger',
              openapi_url='/openapi.json', version='0.4.0')

app.include_router(health.router)
app.include_router(gateway.router)
app.include_router(auth.router)
