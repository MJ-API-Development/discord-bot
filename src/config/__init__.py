from pydantic import BaseSettings, Field


class Logging(BaseSettings):
    filename: str = Field(default="discord.log")


class APPSettings(BaseSettings):
    """APP Confi settings"""
    APP_NAME: str = Field(default="ESA-discord-bot")
    TITLE: str = Field(default="EOD-Stock-API - Financial Data Discord Bot")
    DESCRIPTION: str = Field(
        default="Discord-Bot to send EOD-Stock-API Financial Data to Discord for Promotional Purposes")
    VERSION: str = Field(default="1.0.0")
    TERMS: str = Field(default="https://eod-stock-api.site/terms")
    CONTACT_NAME: str = Field(default="MJ API Development")
    CONTACT_URL: str = Field(default="https://eod-stock-api.site/contact")
    CONTACT_EMAIL: str = Field(default="info@eod-stock-api.site")
    LICENSE_NAME: str = Field(default="Apache 2.0")
    LICENSE_URL: str = Field(default="https://www.apache.org/licenses/LICENSE-2.0.html")
    DOCS_URL: str = Field(default='/docs')
    OPENAPI_URL: str = Field(default='/openapi')
    REDOC_URL: str = Field(default='/redoc')


class DiscordSettings(BaseSettings):
    APPLICATION_ID: str = Field(..., env='DISCORD_APPLICATION_ID')
    PUBLIC_KEY: str = Field(..., env='DISCORD_PUBLIC_KEY')
    INTERACTIONS_ENDPOINT: str = Field(..., env='DISCORD_INTERACTIONS_ENDPOINT')
    LINKED_ROLES_VERIFICATIONS_URL: str = Field(..., env='DISCORD_LINKED_ROLES_VERIFICATIONS_URL')
    TOKEN: str = Field(..., env='DISCORD_TOKEN')
    NEWS_API_CHANNEL_ID: int = Field(..., env='NEWS_API_CHANNEL_ID')
    ADMIN_ID: str = Field(..., env='DISCORD_ADMIN_ID')

    class Config:
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


class Settings(BaseSettings):
    EOD_API_KEY: str = Field(..., env='EOD_STOCK_API_KEY')
    DEVELOPMENT_SERVER_NAME: str = Field(..., env='DEVELOPMENT_SERVER_NAME')
    APP_SETTINGS: APPSettings = APPSettings()
    DISCORD_SETTINGS: DiscordSettings = DiscordSettings()
    LOGGING: Logging = Logging()

    class Config:
        env_file = '.env.development'
        env_file_encoding = 'utf-8'


def config_instance() -> Settings:
    return Settings()
