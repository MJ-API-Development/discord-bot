from typing import List, Dict

import aiohttp
from src.config import config_instance
from src.logger import init_logger
from src.models.articles import NewsArticle
from src.models.stock import Stock


class TasksExecutor:
    def __init__(self):
        self._logger = init_logger(self.__class__.__name__)
        self._params: dict[str, str] = {'api_key': config_instance().EOD_API_KEY}

    async def get_articles_bounded(self, count: int = 10):
        """
        **get_articles**
            create a list of articles that can be used to send tweets
        :return:
        """
        self._logger.info("Fetching Articles from API")
        request_url: str = f"https://gateway.eod-stock-api.site/api/v1/news/articles-bounded/{count}"
        try:
            return await self.do_fetch_articles(request_url)
        except aiohttp.ClientError as e:
            self._logger.error(f"Error fetching articles: {str(e)}")
            return None

    async def list_publishers(self) -> list[str] | None:
        """
        :return:
        """
        self._logger.info("Fetching Publishers from API")
        request_url: str = f"https://gateway.eod-stock-api.site/api/v1/news/list-publishers"
        return await self.return_lists(request_url=request_url)

    async def list_exchanges(self) -> list[str] | None:
        """

        :return:
        """
        self._logger.info("Fetching Exchanges from API")
        request_url: str = f"https://gateway.eod-stock-api.site/api/v1/exchanges"
        return await self.return_lists(request_url=request_url)

    async def return_lists(self, request_url: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=request_url, params=self._params) as response:
                    response.raise_for_status()
                    if response.headers.get('Content-Type') == 'application/json':
                        results = await response.json()
                        return results['payload']
                    return None

        except aiohttp.ClientError as e:
            self._logger.error(f"Error fetching articles: {str(e)}")
            return None

    async def tickers_by_exchange(self, exchange_code: str) -> list[dict[str, str | None]] | None:
        """

        :param exchange_code:
        :return:
        """
        self._logger.info("Fetching Exchanges from API")

        request_url: str = f"https://gateway.eod-stock-api.site/api/v1/stocks/exchange/code/{exchange_code}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=request_url, params=self._params) as response:
                    response.raise_for_status()
                    if response.headers.get('Content-Type') == 'application/json':
                        response = await response.json()
                        return await self.extract_ticker_info(tickers=response.get('payload', []))

                    return None

        except aiohttp.ClientError as e:
            self._logger.error(f"Error fetching articles: {str(e)}")
            return None

    @staticmethod
    async def extract_ticker_info(tickers: list[dict[str, str]]):
        ticker_info = []
        for ticker in tickers:
            code = ticker.get('code')
            name = ticker.get('name')
            if code and name:
                ticker_info.append({'code': code, 'name': name})
        return ticker_info

    @staticmethod
    async def companies_by_exchange(exchange_code: str) -> dict[str, str]:
        """

        :param exchange_code:
        :return:
        """
        return dict(status=False, payload={}, message="Not implemented!")

    async def articles_by_exchange(self, exchange_code: str) -> list[NewsArticle] | None:
        """

        :param exchange_code:
        :return:
        """
        self._logger.info("Fetching Exchanges from API")

        request_url: str = f"https://gateway.eod-stock-api.site/api/v1/news/articles-by-exchange/{exchange_code}"

        try:
            return await self.do_fetch_articles(request_url)

        except aiohttp.ClientError as e:
            self._logger.error(f"Error fetching articles: {str(e)}")
            return None

    async def articles_by_ticker(self, ticker: str) -> list[dict]:
        self._logger.info("Fetching Articles By Ticker from API")
        request_url: str = f"https://gateway.eod-stock-api.site/api/v1/news/articles-by-ticker/{ticker}"

        try:
            return await self.do_fetch_articles(request_url)

        except aiohttp.ClientError as e:
            self._logger.error(f"Error fetching articles: {str(e)}")
            return []

    async def articles_by_page(self, number: int = 1) -> list[dict]:
        self._logger.info("Fetching Articles By Page Number from API")
        request_url: str = f"https://gateway.eod-stock-api.site/api/v1/news/articles-by-page/{number}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=request_url, params=self._params) as response:
                    response.raise_for_status()
                    if response.headers.get('Content-Type') == 'application/json':
                        response = await response.json()
                        articles = response.get('payload', {}).get('results', [])
                        # Format the articles payload to include only title and link
                        return articles
                    return []

        except aiohttp.ClientError as e:
            self._logger.error(f"Error fetching articles: {str(e)}")
            return []

    async def articles_by_publisher(self, publisher: str = None) -> list[NewsArticle]:
        """
        :param publisher:
        :return:
        """
        try:
            request_url: str = f"https://gateway.eod-stock-api.site/api/v1/news/articles-by-publisher/{publisher}"
            return await self.do_fetch_articles(request_url)
        except aiohttp.ClientError as e:
            self._logger.error(f"Error fetching articles: {str(e)}")
            return []

    async def articles_by_date(self, _date: str) -> List[NewsArticle]:
        """

        :param _date:
        :return:
        """
        try:
            request_url: str = f"https://gateway.eod-stock-api.site/api/v1/news/articles-by-date/{_date}"
            return await self.do_fetch_articles(request_url)
        except aiohttp.ClientError as e:
            self._logger.error(f"Error fetching articles: {str(e)}")
            return []

    async def do_fetch_articles(self, request_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url=request_url, params=self._params) as response:
                response.raise_for_status()
                if response.headers.get('Content-Type') == 'application/json':
                    response = await response.json()
                    articles = response.get('payload', [])
                    # Format the articles payload to include only title and link
                    return articles
                return []


tasks_executor = TasksExecutor()
