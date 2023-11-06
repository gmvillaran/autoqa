from elasticapm.contrib.starlette import ElasticAPM
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from restapi.api import api_router
from restapi.core import apm_client, logger, settings
from vectorstore.connector import monitor

app = FastAPI(title=settings.PROJECT_NAME)
tz = settings.TIMEZONE
origins = ["*"]

monitor.logger = logger
client = monitor.client

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if apm_client is not None:
    app.add_middleware(ElasticAPM, client=apm_client)

app.include_router(api_router, prefix=settings.API_STR)


@app.on_event("startup")
async def startup_event():
    monitor.start()


@app.get("/")
async def docs_redirect():
    logger.info("Redirecting to docs")
    return RedirectResponse(url="/docs")
