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

import httpx
from datetime import datetime
from http.cookiejar import CookieJar, Cookie

from li_scrapi.cookie_repository import (
    CookieRepository,
    LinkedinSessionExpired,
)


def mock_cookies(date=datetime.strptime("2050-05-04", "%Y-%m-%d")):
    cookie = Cookie(
        version=None,
        domain_initial_dot=True,
        rest={},
        comment="",
        comment_url="",
        name="JSESSIONID",
        port=None,
        port_specified=False,
        value="1234",
        expires=int(date.timestamp()),
        domain="httpbin.org",
        domain_specified=True,
        path="/cookies",
        path_specified=True,
        secure=False,
        discard=False,
    )
    cookie_jar = CookieJar()
    cookie_jar.set_cookie(cookie)
    return httpx.Cookies(cookie_jar)


def test_save():
    repo = CookieRepository()
    repo.set_cookies_dir()
    repo.save(mock_cookies(), "testuser")
    assert True


def test_get():
    repo = CookieRepository()
    repo.set_cookies_dir()
    c = repo.get("testuser")
    assert c is not None
    assert c == mock_cookies()


def test_get_nonexistent_file():
    repo = CookieRepository()
    repo.set_cookies_dir()
    c = repo.get("ghost")
    assert len(c) == 0


def test_get_expired():
    repo = CookieRepository()
    repo.set_cookies_dir()
    repo.save(
        mock_cookies(date=datetime.strptime("2001-05-04", "%Y-%m-%d")), "testuserex"
    )
    try:
        repo.get("testuserex")
        assert False
    except LinkedinSessionExpired:
        assert True
