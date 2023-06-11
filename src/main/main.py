import asyncio
from json.decoder import JSONDecodeError
from fastapi import FastAPI, Path
from fastapi.responses import JSONResponse
from src.config import config_instance
from src.logger import init_logger, AppLogger
from src.commander import client, command_processor

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
task_started = False

logger = init_logger("Discord-BOt")


@app.on_event("startup")
async def startup_event():
    global task_started
    if not task_started:
        # Set the flag to indicate that the task has started
        task_started = True
        # Start the task
        asyncio.create_task(client.start(token=settings.TOKEN))
        logger.info("Discord bot running")
    else:
        logger.info("Task already started, skipping...")

    # TODO create a link clean up event


@app.get('/resource/{path}')
async def get_resource(path: str = Path(...)):
    resource_key = str(path)
    logger.info(f"path is {resource_key}")
    try:
        response = await command_processor.get_resource_by_key(resource_key=resource_key)
        _content = dict(payload=response, message='successfully retrieved data')
        return JSONResponse(content=_content, status_code=200, headers={"Content-Type": "application/json"})
    except JSONDecodeError as e:
        logger.error(str(e))
        _response = {"message": "Error reading response"}
        return JSONResponse(content=_response, status_code=500, headers={"Content-Type": "application/json"})
