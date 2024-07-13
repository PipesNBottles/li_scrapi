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

import os
import time
import li_scrapi.utils.settings as settings
from http.cookiejar import CookieJar, MozillaCookieJar
from httpx import Cookies
from li_scrapi.utils.errors import LinkedinSessionExpired


class CookieRepository:
    """
    Class to act as a repository for the cookies.
    """

    def __init__(self):
        self.cookie_jar = MozillaCookieJar()

    def set_cookies_dir(self, cookies_dir=settings.COOKIE_PATH):
        self.cookies_dir = cookies_dir or settings.COOKIE_PATH

    def save(self, cookies: Cookies, username: str):
        self._ensure_cookies_dir()
        cookiejar_filepath = self._get_cookies_filepath(username)
        for cookie in cookies.jar:
            self.cookie_jar.set_cookie(cookie)
        self.cookie_jar.save(cookiejar_filepath)

    def get(self, username: str) -> Cookies:
        cookies = self._load_cookies_from_cache(username)
        if cookies and not CookieRepository._is_token_still_valid(cookies.jar):
            raise LinkedinSessionExpired
        return cookies

    def _ensure_cookies_dir(self):
        if not os.path.exists(self.cookies_dir):
            os.makedirs(self.cookies_dir)

    def _get_cookies_filepath(self, username) -> str:
        """
        Return the absolute path of the cookiejar for a given username
        """
        return "{}{}.txt".format(self.cookies_dir, username)

    def _load_cookies_from_cache(self, username: str) -> Cookies:
        cookie_jar = None
        cookiejar_filepath = self._get_cookies_filepath(username)
        if os.path.exists(cookiejar_filepath):
            self.cookie_jar.load(cookiejar_filepath)
            cookie_jar = self.cookie_jar
        return Cookies(cookie_jar)

    @staticmethod
    def _is_token_still_valid(cookiejar: CookieJar):
        _now = time.time()
        for cookie in cookiejar:
            if cookie.name == "JSESSIONID" and cookie.value:
                if cookie.expires and cookie.expires > _now:
                    return True
            if cookie.name == "li_at" and cookie.value:
                if cookie.expires and cookie.expires > _now:
                    return True

        return False
