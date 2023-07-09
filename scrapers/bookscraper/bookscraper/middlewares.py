# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from collections.abc import Mapping
from typing import Any
import random
from urllib.parse import urlencode
import requests
import base64

import scrapy
from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class BookscraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class BookscraperDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

class ScrapeOpsFakeUserAgentMiddleware:
    """
    Middleware that randomly selects user agent and modifies request.
    """
    @classmethod
    def from_crawler(cls, crawler: scrapy.Spider):
        """
        Get settings from crawler

        :param: crawler - scrapy spider object
        :dtype: scrapy.Spider
        :return: parsed crawler settings
        """
        return cls(crawler.settings)

    def __init__(self, settings: Mapping[str, Any]) -> None:
        self.api_key = settings.get("API_KEY")
        self.endpoint = settings.get("FAKE_USER_AGENT_ENDPOINT", "https://headers.scrapeops.io/v1/user-agents")
        self.enabled_fake_user_agents = settings.get("FAKE_USER_AGENT_ENABLED", False)
        self.num_results = settings.get("NUM_RESULTS")

        self.headers = []
        self._get_user_agents()
        self._fake_user_agents_enabled()

    def _get_user_agents(self) -> None:
        """
        Retrieve list of user agents from ScrapeOps

        :return: None
        :rtype: None
        """
        payload = {"api_key": self.api_key}
        if self.num_results is not None:
            payload["num_results"] = self.num_results

        response = requests.get(self.endpoint, params=urlencode(payload)).json()
        self.user_agents = [response.get("result", [])]

    def _get_random_user_agent(self) -> str:
        """
        Get random user agent from list

        :return: user-agent string
        :rtype: str
        """
        return self.user_agents[random.randint(0, len(self.user_agents)-1)]

    def _fake_user_agents_enabled(self) -> None:
        """
        Toggle flag to set user agents as active or not

        :return: None
        :rtype: None
        """
        if self.api_key is None or self.api_key == "" or not self.enabled_fake_user_agents:
            self.enabled_fake_user_agents = False
        else:
            self.enabled_fake_user_agents = True

    def process_request(self, request: scrapy.http.headers.Headers, spider: scrapy.Spider) -> None:
        """
        Randomly select user agent add to request header.

        :param: request - request object
        :dtype: scrapy.http.headers.Headers
        :param: spider - scrapy spider
        :dtype: scrapy.Spider
        :return: None
        :rtype: None
        """
        # Randomly select user agent
        user_agent = self._get_random_user_agent()
        request.headers["User-Agent"] = user_agent

class ScrapeOpsFakeBrowserHeaderAgentMiddleware:
    """
    Middleware that generates fake browser header before request is sent.
    """
    @classmethod
    def from_crawler(cls, crawler: scrapy.Spider):
        """
        Get settings from crawler

        :param: crawler - scrapy spider object
        :dtype: scrapy.Spider
        :return: parsed crawler settings
        """
        return cls(crawler.settings)

    def __init__(self, settings: Mapping[str, Any]) -> None:
        self.api_key = settings.get('API_KEY')
        self.endpoint = settings.get('FAKE_BROWSER_HEADER_ENDPOINT', 'http://headers.scrapeops.io/v1/browser-headers')
        self.enabled_fake_browser_headers= settings.get('FAKE_BROWSER_HEADER_ENABLED', False)
        self.num_results = settings.get('NUM_RESULTS')
        self.headers = []
        self._get_headers()
        self._fake_browser_headers_enabled()

    def _get_headers(self):
        """
        Get headers from ScrapeOps
        """
        payload = {"api_key": self.api_key}
        if self.num_results is not None:
            payload["num_results"] = self.num_results
        response = requests.get(self.endpoint, params=urlencode(payload)).json()
        self.headers = response.get("result", [])

    def _get_random_browser_header(self) -> dict[str, Any]:
        """
        Randomly select browser header.

        :return: fake header
        :rtype: dict[str, Any]
        """
        return self.headers[random.randint(0, len(self.headers) - 1)]

    def _fake_browser_headers_enabled(self):
        """
        Toggle setting to use fake browser headers

        :return: None
        :rtype: None
        """
        if self.api_key is None or self.api_key == '' or not self.enabled_fake_browser_headers:
            self.enabled_fake_browser_headers = False
        else:
            self.enabled_fake_browser_headers = True

    def process_request(self, request: scrapy.http.headers.Headers, spider: scrapy.Spider) -> None:
        """
        Randomly select fake browser header

        :param: request - request object
        :dtype: scrapy.http.headers.Header
        :param: spider - scrapy spider
        :dtype: scrapy.Spider
        :return: None
        :rtype: None
        """
        random_browser_header = self._get_random_browser_header()
        request = request.replace(headers=random_browser_header)

class MyProxyMiddleware(object):
    """
    Middleware for updating proxy.
    """
    @classmethod
    def from_crawler(cls, crawler: scrapy.Spider):
        """
        Get settings from crawler

        :param: crawler - scrapy spider object
        :dtype: scrapy.Spider
        :return: parsed crawler settings
        """
        return cls(crawler.settings)

    def __init__(self, settings: Mapping[str, Any]):
        self.user = settings.get("PROXY_USER")
        self.password = settings.get("PROXY_PASSWORD")
        self.endpoint = settings.get("PROXY_ENDPOINT")
        self.port = settings.get("PROXY_PORT")

    def process_request(self, request: scrapy.http.headers.Headers, spider: scrapy.Spider):
        """
        Sets up proxy and proxy authorization in the request header.

        :param: request - request object
        :dtype: scrapy.http.headers.Headers
        :param: spider - scrapy spider
        :dtype: scrapy.Spider
        :return: None
        :rtype: None
        """
        user_credentials = f"{self.user}:{self.password}"
        basic_authentication = "Basic " + base64.b64encode(user_credentials.encode()).decode()
        host = f"http://{self.endpoint}:{self.port}"
        request.meta["proxy"] = host
        request.headers['Proxy-Authorization'] = basic_authentication