import asyncio
import concurrent.futures
from fastapi import FastAPI, Path
from src.config import config_instance
from src.logger import init_logger, AppLogger
from src.commander import client

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

TEN_MINUTES = 600
settings = config_instance().DISCORD_SETTINGS


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(client.start(token=settings.TOKEN))
    print("Discord bot running")


