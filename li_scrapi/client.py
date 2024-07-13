"""
MIT License

Copyright (c) 2024 Tom Quirk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from httpx import _client, Cookies, Response
from bs4 import BeautifulSoup, Tag
from li_scrapi.cookie_repository import CookieRepository
from li_scrapi.utils.errors import ChallengeException, UnauthorizedException
from tenacity import (
    retry,
    wait_exponential_jitter,
    stop_after_attempt,
    retry_if_not_result,
)
from abc import ABC, abstractmethod
from aiolimiter import AsyncLimiter

import loguru
import json
import http


class Client(ABC):
    # Settings for general Linkedin API calls
    LINKEDIN_BASE_URL = "https://www.linkedin.com"
    API_BASE_URL = f"{LINKEDIN_BASE_URL}/voyager/api"
    REQUEST_HEADERS = {
        "user-agent": " ".join(
            [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5)",
                "AppleWebKit/537.36 (KHTML, like Gecko)",
                "Chrome/83.0.4103.116 Safari/537.36",
            ]
        ),
        # "accept": "application/vnd.linkedin.normalized+json+2.1",
        "accept-language": "en-AU,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
        "x-li-lang": "en_US",
        "x-restli-protocol-version": "2.0.0",
        # "x-li-track": '{"clientVersion":"1.2.6216","osName":"web","timezoneOffset":10,"deviceFormFactor":"DESKTOP","mpName":"voyager-web"}',
    }

    # Settings for authenticating with Linkedin
    AUTH_REQUEST_HEADERS = {
        "X-Li-User-Agent": "LIAuthLibrary:0.0.3 com.linkedin.android:4.1.881 Asus_ASUS_Z01QD:android_9",
        "User-Agent": "ANDROID OS",
        "X-User-Language": "en",
        "X-User-Locale": "en_US",
        "Accept-Language": "en-us",
    }

    logger = loguru.logger
    _cookie_repository = CookieRepository()

    @abstractmethod
    def __init__(
        self, session: _client.BaseClient, cookies_dir: str, refresh_cookies=False
    ):
        self._session: _client.BaseClient
        self.metadata: dict

    @property
    def cookies(self):
        return self._session.cookies

    def _set_session_cookies(self, cookies: Cookies):
        """
        Set cookies of the current session and save them to a file named as the username.
        """
        self._session.cookies = cookies
        if "li_at" in cookies:
            self._session.headers["li_at"] = self._session.cookies["li_at"]
        if "JSESSIONID" in cookies:
            self._session.headers["csrf-token"] = self._session.cookies[
                "JSESSIONID"
            ].strip('"')

    def _parse_metadata(self, soup: BeautifulSoup):
        clientApplicationInstanceRaw = soup.find(
            "meta", attrs={"name": "applicationInstance"}
        )
        if clientApplicationInstanceRaw and isinstance(
            clientApplicationInstanceRaw, Tag
        ):
            raw_content = clientApplicationInstanceRaw.attrs.get("content", {})
            clientApplicationInstance = json.loads(raw_content)
            self.metadata["clientApplicationInstance"] = clientApplicationInstance

        clientPageInstanceIdRaw = soup.find(
            "meta", attrs={"name": "clientPageInstanceId"}
        )
        if clientPageInstanceIdRaw and isinstance(clientPageInstanceIdRaw, Tag):
            clientPageInstanceId = clientPageInstanceIdRaw.attrs.get("content", {})
            self.metadata["clientPageInstanceId"] = clientPageInstanceId

    @staticmethod
    def _has_failed(value):
        Client.logger.debug(
            f"status code of {value.request.url} \n is {value.status_code} if not 200, \n retry ..."
        )
        return value.status_code == http.HTTPStatus.OK

    @abstractmethod
    def get(self, url: str, **kwargs) -> Response: ...

    @abstractmethod
    def post(self, url: str, **kwargs) -> Response: ...

    @abstractmethod
    def authenticate(self, username: str, password: str): ...

    @abstractmethod
    def close(self): ...


class LinkedInClient(Client):
    """
    Class to act as a client for the Linkedin API.
    """

    def __init__(
        self, session: _client.Client, cookies_dir: str = "", refresh_cookies=False
    ):
        self._session: _client.Client = session
        self._session.headers.update(self.REQUEST_HEADERS)
        self.metadata = {}
        self._use_cookie_cache = not refresh_cookies
        self._cookie_repository.set_cookies_dir(cookies_dir)

    def close(self):
        self._session.close()

    def _request_session_cookies(self):
        """
        Return a new set of session cookies as given by Linkedin.
        """
        self.logger.debug("Requesting new cookies.")
        res = self.get(
            f"{self.LINKEDIN_BASE_URL}/uas/authenticate",
            headers=self.AUTH_REQUEST_HEADERS,
        )
        return res.cookies

    def authenticate(self, username: str, password: str):
        if self._use_cookie_cache:
            self.logger.debug("Attempting to use cached cookies")
            cookies = self._cookie_repository.get(username)
            if cookies:
                self.logger.debug("Using cached cookies")
                self._set_session_cookies(cookies)
                self._fetch_metadata()
                return

        self._do_authentication_request(username, password)
        self._fetch_metadata()

    def _fetch_metadata(self):
        """
        Get metadata about the "instance" of the LinkedIn application for the signed in user.

        Store this data in self.metadata
        """
        res = self._session.get(
            f"{self.LINKEDIN_BASE_URL}",
            cookies=self._session.cookies,
            headers=self.AUTH_REQUEST_HEADERS,
        )

        soup = BeautifulSoup(res.text, "lxml")
        self._parse_metadata(soup)

    def _do_authentication_request(self, username: str, password: str):
        """
        Authenticate with Linkedin.

        Return a session object that is authenticated.
        """
        self._set_session_cookies(self._request_session_cookies())

        payload = {
            "session_key": username,
            "session_password": password,
            "JSESSIONID": self._session.cookies["JSESSIONID"],
        }

        res = self.post(
            f"{self.LINKEDIN_BASE_URL}/uas/authenticate",
            data=payload,
            headers=self.AUTH_REQUEST_HEADERS,
            cookies=self._session.cookies,
        )

        if res.status_code > http.HTTPStatus.OK:
            raise UnauthorizedException()

        data = res.json()

        if data and data["login_result"] != "PASS":
            raise ChallengeException(data["login_result"])

        self._set_session_cookies(res.cookies)
        res.request.url
        self._cookie_repository.save(res.cookies, username)

    @retry(
        wait=wait_exponential_jitter(2, 15),
        stop=stop_after_attempt(5),
        retry=retry_if_not_result(Client._has_failed),
        retry_error_callback=lambda x: x.outcome.result(),  # type: ignore
    )  # type: ignore
    def post(self, url: str, **kwargs):
        return self._session.post(url, **kwargs)

    @retry(
        wait=wait_exponential_jitter(2, 15),
        stop=stop_after_attempt(5),
        retry=retry_if_not_result(Client._has_failed),
        retry_error_callback=lambda x: x.outcome.result(),  # type: ignore
    )  # type: ignore
    def get(self, url: str, **kwargs):
        return self._session.get(url, **kwargs)


class AsyncLinkedInClient(Client):
    def __init__(
        self, session: _client.AsyncClient, cookies_dir: str = "", refresh_cookies=False
    ):
        self._session: _client.AsyncClient = session
        self._session.headers.update(self.REQUEST_HEADERS)
        self.metadata = {}
        self._use_cookie_cache = not refresh_cookies
        self._cookie_repository.set_cookies_dir(cookies_dir)
        self._limiter = AsyncLimiter(200, 60)

    async def close(self):
        await self._session.aclose()

    async def _request_session_cookies(self):
        """
        Return a new set of session cookies as given by Linkedin.
        """
        self.logger.debug("Requesting new cookies.")

        res = await self._session.get(
            f"{self.LINKEDIN_BASE_URL}/uas/authenticate",
            headers=self.AUTH_REQUEST_HEADERS,
        )
        return res.cookies

    async def authenticate(self, username: str, password: str):
        if self._use_cookie_cache:
            self.logger.debug("Attempting to use cached cookies")
            cookies = self._cookie_repository.get(username)
            if cookies:
                self.logger.debug("Using cached cookies")
                self._set_session_cookies(cookies)
                await self._fetch_metadata()
                return

        await self._do_authentication_request(username, password)
        await self._fetch_metadata()

    async def _fetch_metadata(self):
        """
        Get metadata about the "instance" of the LinkedIn application for the signed in user.

        Store this data in self.metadata
        """
        res = await self._session.get(
            f"{self.LINKEDIN_BASE_URL}",
            cookies=self._session.cookies,
            headers=self.AUTH_REQUEST_HEADERS,
        )

        soup = BeautifulSoup(res.text, "lxml")
        self._parse_metadata(soup)

    async def _do_authentication_request(self, username: str, password: str):
        """
        Authenticate with Linkedin.

        Return a session object that is authenticated.
        """
        self._set_session_cookies(await self._request_session_cookies())

        payload = {
            "session_key": username,
            "session_password": password,
            "JSESSIONID": self._session.cookies["JSESSIONID"],
        }

        res = await self._session.post(
            f"{self.LINKEDIN_BASE_URL}/uas/authenticate",
            data=payload,
            cookies=self._session.cookies,
            headers=self.AUTH_REQUEST_HEADERS,
        )

        if res.status_code > http.HTTPStatus.OK:
            raise UnauthorizedException()

        data = res.json()

        if data and data["login_result"] != "PASS":
            raise ChallengeException(data["login_result"])

        self._set_session_cookies(res.cookies)
        self._cookie_repository.save(res.cookies, username)

    @retry(
        wait=wait_exponential_jitter(2, 15),
        stop=stop_after_attempt(5),
        retry=retry_if_not_result(Client._has_failed),
        retry_error_callback=lambda x: x.outcome.result(),  # type: ignore
    )  # type: ignore
    async def post(self, url: str, **kwargs):
        async with self._limiter:
            return await self._session.post(url, **kwargs)

    @retry(
        wait=wait_exponential_jitter(2, 15),
        stop=stop_after_attempt(5),
        retry=retry_if_not_result(Client._has_failed),
        retry_error_callback=lambda x: x.outcome.result(),  # type: ignore
    )  # type: ignore
    async def get(self, url: str, **kwargs):
        async with self._limiter:
            return await self._session.get(url, **kwargs)
