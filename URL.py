from requests import Session, head
from requests_html import HTMLSession
from requests_cache import CachedSession
from os import path as ospath
from os import mkdir


htmlsession = HTMLSession()
invalid_chars = [
    ":",
    "/",
    "\\",
    "|",
    "*",
    "?",
    "<",
    ">",
    '"',
]  # Characters that are forbidden in file/folder names


class URL:
    def __init__(self, url: str, cache=False, expire_after=120):
        self.url = url
        self.domain = url.rsplit("/", 1)[0]
        self.filename = url.rsplit("/", 1)[1].split("?")[0]

        try:
            self.ext = "." + self.filename.rsplit(".", 1)[1]
        except:
            self.ext = None

        if cache == True:
            self.session = CachedSession(expire_after)
        if cache == False:
            self.session = Session()

        self.htmlsession = HTMLSession()

    def __str__(self):
        return self.url

    @property
    def size(self):
        try:
            self._size = head(self.url).headers["Content-Length"]
        except Exception as e:
            self._size = None
        return self._size

    def get(self, proxies=None) -> bytes:
        """return url content in bytes"""
        self.content = self.session.get(
            self.url, stream=True, allow_redirects=True, proxies=proxies
        ).content
        return self.content

    def render(self, timeout=None) -> str:
        """run javascript and return html in str format"""
        timeout = 60 if timeout == None else timeout
        r = self.htmlsession.get(self.url)
        r.html.render(timeout=timeout)
        self.rendered_content = r.html.html
        return self.rendered_content

    def download(
        self,
        path=None,
        directory=None,
        ext=None,
        replace=False,
        log=False,
        proxies=None,
    ):
        """download and save url content"""
        if path == None:
            directory = None
            path = "".join(ch for ch in self.filename if ch not in invalid_chars).strip()

        if directory != None:
            try:
                os.mkdir(directory)
                path = directory + "/" + self.filename
            except Exception as e:
                raise e

        if ext != None:
            path += ext

        if log == True:
            print(f'Downloading "{path}"...')

        if replace == False and ospath.exists(path):
            pass

        else:
            r = self.get(proxies=proxies)
            with open(path, "wb") as fp:
                fp.write(r)
