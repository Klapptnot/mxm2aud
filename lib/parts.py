"""Classes and functions from/for the main script"""

import re
import sys
import urllib.parse
import urllib3
import json5


class DataNotAvailable(Exception):
    """Exception raised when data could not be found"""

    def __init__(self, message):
        self.message = message

    def __str__(self) -> str:
        # return super().__str__()
        return self.message


class Song:
    """Idk. Tools to get-extract song URLs and data from network resources"""

    def __init__(
        self,
        timeout: int = 1,
        tries: int = 1,
        user_agent: str = None,
        cookies: str = None,
    ):
        if timeout == 0 or tries == 0:
            raise ValueError("Timeout o Tries cannot be 0")
        self.user_agent = user_agent if user_agent else "Parts Lib V19.2"
        self.cookies = cookies if cookies else "None"
        self.timeout = timeout if timeout else 1
        self.tries = tries if tries else 1

    def check_url(self, url: str = None) -> bool:
        """Just checks if a url is valid for this use"""
        if url is None:
            return False
        url_dig = re.match(r"(?:https?://)?(?:.*\.)?([a-z0-9.-]+)\.com", url)
        if not url_dig:
            return False
        if url_dig.group(1) != "musixmatch":
            return False
        return True

    def request(self, url: str = None, headers: dict = None, method: str = "GET"):
        """Request a network resource without using the requests module"""
        if url is None:
            raise ValueError("URL must not be None")
        http = urllib3.PoolManager()
        return http.request(method, url, headers=headers)

    def replace_user_agent(self, user_agent: str = None):
        """Try to change the user agent set by the constructor"""
        self.user_agent = user_agent if user_agent else "Parts Lib V19.2"

    def replace_cookies(self, cookies: str = None):
        """Try to change the cookies string set by the constructor
        Only used to get data from Musixmatch"""
        self.cookies = cookies if cookies else "None"

    def replace_times(self, timeout: str = 1, tries: str = 1):
        """Try to change timeout and tries values set by constructor"""
        if timeout == 0 or tries == 0:
            raise ValueError("Timeout o Tries cannot be 0")
        self.timeout = timeout if timeout else 1
        self.tries = tries if tries else 1

    def get_urls(self, keyword: str = None, index: int = None) -> list[str] | str:
        """
        Returns a list with URLs strings or one url to Musixmatch (Expected to be)
        """
        if keyword is None:
            raise ValueError("Keyword is None")
        keyword = f"{keyword} lyrics site:musixmatch.com"
        url = f"https://google.com/search?q={urllib.parse.quote(keyword)}"
        for _ in range(self.tries):
            res = self.request(
                url,
                headers={"User-Agent": self.user_agent},
            )
            if res.status == 200:
                break
        if res.status != 200:
            raise DataNotAvailable("Unexpected status code")
        url_list = []
        # Get and sanitize url
        for url in re.findall(
            r'<div class="yuRUbf"><div><span jscontroller="msmzHf" jsaction="rcuQ6b:npT2md;PYDNKe:bLV6Bd;mLt3mc"><a jsname="UWckNb" href="[^ ]*',
            res.data.decode("utf-8"),
        ):
            idx = url.find("/translation")
            if idx != -1:
                url_list.append(
                    re.sub(
                        r'<div class="yuRUbf"><div><span jscontroller="msmzHf" jsaction="rcuQ6b:npT2md;PYDNKe:bLV6Bd;mLt3mc"><a jsname="UWckNb" href="',
                        "",
                        url[:idx],
                    ).rstrip('"')
                )
            else:
                url_list.append(
                    re.sub(
                        r'<div class="yuRUbf"><div><span jscontroller="msmzHf" jsaction="rcuQ6b:npT2md;PYDNKe:bLV6Bd;mLt3mc"><a jsname="UWckNb" href="',
                        "",
                        url,
                    ).rstrip('"')
                )
        if not url_list:
            raise DataNotAvailable("Zero URLs were found")
        if index is not None:
            return url_list[0]
        return url_list

    def get_data(self, url: str = None, deserialize: bool = True) -> str | dict:
        """
        Returns a JSON string or Python object with song info from Musixmatch [url]
        """
        if url is None:
            raise ValueError("URL in None")
        for _ in range(self.tries):
            res = self.request(
                url,
                headers={"User-Agent": self.user_agent, "Cookies": self.cookies},
            )
            if res.status == 200:
                break
        if res.status != 200:
            raise DataNotAvailable("Unexpected status code")
        match = re.search(
            r"(?<=var __mxmState = ).*(?=;</script>)", res.data.decode("utf-8")
        )
        if not match:
            raise DataNotAvailable("Could not find data in response")
        if deserialize:
            return json5.loads(match.group())
        return match.group()

    def get_res(self, keyword: str = None, index: int = 0) -> dict:
        """
        Returns a Python object with song info from Musixmatch [url] using a keyword to search
        """
        if keyword is None:
            raise ValueError("Keyword cannot be None")
        try:
            url = self.get_urls(keyword=keyword)[index]
        except DataNotAvailable as e_data:
            print(f"No URLs found for {keyword}: {e_data}")
            sys.exit(2)
        try:
            data = self.get_data(url=url, deserialize=True)
        except DataNotAvailable as e_data:
            print(f"Sorry, we don't have enough data: {e_data}")
            sys.exit(1)
        return data
