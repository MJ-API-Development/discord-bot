import asyncio

from fastapi import FastAPI
from src.config import config_instance
from src.logger import init_logger, AppLogger
from src.scheduler import TaskScheduler, client

settings = config_instance().APP_SETTINGS
app = FastAPI(
    title=settings.TITLE,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    terms_of_service=settings.TERMS,
    contact={
        "name": settings.CONTACT_NAME,
        "url": settings.CONTACT_URL,
        "email": settings.CONTACT_EMAIL
    },
    license_info={
        "name": settings.LICENSE_NAME,
        "url": settings.LICENSE_URL,
    },
    docs_url=settings.DOCS_URL,
    openapi_url=settings.OPENAPI_URL,
    redoc_url=settings.REDOC_URL
)

scheduler = TaskScheduler()

# this allows me to send 30 tweets over a period of 24 hours

TEN_MINUTES = 600
settings = config_instance().DISCORD_SETTINGS


asyncio.create_task(client.run(token=settings.TOKEN, log_handler=AppLogger(name="Discord").handler))


@app.on_event("startup")
async def startup_event():
    # asyncio.create_task(client.run(token=settings.TOKEN))
    pass


