
from datetime import datetime
from pydantic import BaseModel, Field


class Thumbnail(BaseModel):
    url: str
    width: int
    height: int
    tag: str


# noinspection PyMethodParameters
class NewsArticle(BaseModel):
    """
    **NewsArticle**
        Used to parse YFinance Articles
    """
    uuid: str
    title: str
    publisher: str | None
    link: str
    providerPublishTime: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    type: str = Field(default='Story')
    thumbnail: list[Thumbnail] | None
    relatedTickers: list[str] | None

    summary: str | None
    body: str | None

    class Config:
        title = "YFinance Article Model"
