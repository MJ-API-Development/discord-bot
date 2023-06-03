
import aiohttp
from src.config import config_instance
from src.logger import init_logger


class TasksExecutor:
    def __init__(self):
        self._logger = init_logger(self.__class__.__name__)

    async def get_articles_bounded(self, count: int = 10):
        """
        **get_articles**
            create a list of articles that can be used to send tweets
        :return:
        """
        self._logger.info("Fetching Articles from API")
        _params: dict[str, str] = {'api_key': config_instance().EOD_API_KEY}
        articles_url: str = f"https://gateway.eod-stock-api.site/api/v1/news/articles-bounded/{count}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=articles_url, params=_params) as response:
                    response.raise_for_status()
                    if response.headers.get('Content-Type') == 'application/json':
                        return await response.json()
                    return None

        except aiohttp.ClientError as e:
            self._logger.error(f"Error fetching articles: {str(e)}")
            return None


