import json
from http.cookiejar import CookieJar, Cookie
from pathlib import Path
from typing import Tuple, Dict
from urllib.parse import urljoin

import pip._vendor.pkg_resources as pkg_resources
import pip._vendor.requests as requests
from pip._vendor.requests.cookies import RequestsCookieJar

BASE_URL = 'https://dnevnik2.petersburgedu.ru/'

REFERRERS = {
    '/api/user/auth/login': '/login',
}


def make_session() -> requests.Session:
    headers_path = Path(pkg_resources.resource_filename(__name__, '../headers.json'))
    if not headers_path.exists():
        raise ValueError(f'headers file {headers_path} is missing')
    with headers_path.open('r', encoding='utf-8') as f1:
        headers = json.load(f1)
    session = requests.Session()
    session.headers.update(headers)
    return session


class Dnevnik2:
    def __init__(self, cookie_jar: CookieJar, base_url: str = BASE_URL):
        self.base_url = base_url
        self._session = make_session()
        self._session.cookies.update(cookie_jar)

    @staticmethod
    def _make_url_and_referer(path: str, base_url: str) -> Tuple[str, Dict[str, str]]:
        headers = {}
        url = urljoin(base_url, path)
        if path in REFERRERS:
            headers['Referer'] = urljoin(base_url, REFERRERS[path])
        return url, headers

    @classmethod
    def make_from_login_by_email(cls, email: str, password: str, base_url: str = BASE_URL) -> 'Dnevnik2':
        auth_data = {"type": "email", "login": email, "activation_code": None, "password": password, "_isEmpty": False}
        session = make_session()
        url, headers = cls._make_url_and_referer('/api/user/auth/login', base_url)
        with session.post(url, json=auth_data, headers=headers) as res:
            if 400 <= res.status_code < 500:
                raise ValueError('Some client error. Most probably login or password is wrong.')
            res.raise_for_status()
        dnevnik: 'Dnevnik2' = cls(session.cookies, base_url=base_url)
        return dnevnik

    @classmethod
    def make_from_cookies_file(cls, cookies_path: Path, base_url: str = BASE_URL) -> 'Dnevnik2':
        if not cookies_path.exists():
            raise ValueError(f"file {cookies_path} doesn't exist")
        with cookies_path.open('r', encoding='utf-8') as f1:
            cookies = json.load(f1)
        cookies_jar = RequestsCookieJar()
        for item in cookies:
            cookies_jar.set(**item)

        return cls(cookies_jar, base_url)

    def save_cookies(self, path: Path):
        cookies = []
        cookie: Cookie
        for cookie in self._session.cookies:
            cookies.append({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'expires': cookie.expires,
            })
        with path.open('w', encoding='utf-8') as f1:
            json.dump(cookies, f1, indent=2, ensure_ascii=True)
