from typing import List, Dict

import aiohttp
from src.config import config_instance
from src.logger import init_logger
from src.models.articles import NewsArticle
from src.models.stock import Stock


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

    async def list_publishers(self) -> list[str] | None:
        """

        :return:
        """
        self._logger.info("Fetching Publishers from API")
        _params: dict[str, str] = {'api_key': config_instance().EOD_API_KEY}
        articles_url: str = f"https://gateway.eod-stock-api.site/api/v1/news/list-publishers"

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

    async def list_exchanges(self) -> list[str] | None:
        """

        :return:
        """
        self._logger.info("Fetching Exchanges from API")
        _params: dict[str, str] = {'api_key': config_instance().EOD_API_KEY}
        articles_url: str = f"https://gateway.eod-stock-api.site/api/v1/exchanges"

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

    async def tickers_by_exchange(self, exchange_code: str) -> list[dict[str, str | None]] | None:
        """

        :param exchange_code:
        :return:
        """
        self._logger.info("Fetching Exchanges from API")
        _params: dict[str, str] = {'api_key': config_instance().EOD_API_KEY}
        request_url: str = f"https://gateway.eod-stock-api.site/api/v1/stocks/exchange/code/{exchange_code}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=request_url, params=_params) as response:
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

    async def companies_by_exchange(self, exchange_code: str) -> dict[str, str]:
        """

        :param exchange_code:
        :return:
        """
        return dict(status=False, payload={}, message="Not implemented!")

    async def articles_by_exchange(self, exchange_code: str) -> list[NewsArticle]:
        """

        :param exchange_code:
        :return:
        """
        self._logger.info("Fetching Exchanges from API")
        _params: dict[str, str] = {'api_key': config_instance().EOD_API_KEY}
        request_url: str = f"https://gateway.eod-stock-api.site/api/v1/news/articles-by-exchange/{exchange_code}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=request_url, params=_params) as response:
                    response.raise_for_status()
                    if response.headers.get('Content-Type') == 'application/json':
                        return await response.json()
                    return None

        except aiohttp.ClientError as e:
            self._logger.error(f"Error fetching articles: {str(e)}")
            return None

    async def articles_by_ticker(self, ticker: str) -> list[NewsArticle]:
        """

        :param exchange_code:
        :return:
        """
        self._logger.info("Fetching Exchanges from API")
        _params: dict[str, str] = {'api_key': config_instance().EOD_API_KEY}
        request_url: str = f"https://gateway.eod-stock-api.site/api/v1/news/articles-by-ticker/{ticker}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=request_url, params=_params) as response:
                    response.raise_for_status()
                    if response.headers.get('Content-Type') == 'application/json':
                        return await response.json()
                    return None

        except aiohttp.ClientError as e:
            self._logger.error(f"Error fetching articles: {str(e)}")
            return None


tasks_executor = TasksExecutor()
