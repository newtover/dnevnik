import datetime as dt
import json
from http.cookiejar import CookieJar, Cookie
from pathlib import Path
from typing import Tuple, Dict, Optional, Union
from urllib.parse import urljoin

import pip._vendor.pkg_resources as pkg_resources
import pip._vendor.requests as requests
from pip._vendor.requests.cookies import RequestsCookieJar

BASE_URL = 'https://dnevnik2.petersburgedu.ru/'

REFERRERS = {
    '/api/user/auth/login': '/login',
    '/api/journal/person/related-child-list': '/students/my',
    '/api/journal/group/related-group-list': '/estimate',
    '/api/group/group/get-list-period': '/estimate',
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


def date_to_str(date: dt.date) -> str:
    return f'{date.day}.{date.month}.{date.year}'


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

    def fetch_children_list(self) -> dict:
        """Fetch the list of children for whom marks are tracked.
        """
        path = '/api/journal/person/related-child-list'
        return self._fetch_json_for_path(path)

    def _fetch_json_for_path(self, path: str, params: Optional[Dict[str, Union[int, str]]] = None) -> dict:
        url, headers = self._make_url_and_referer(path, self.base_url)
        with self._session.get(url, params=params, headers=headers) as res:
            res.raise_for_status()
            return res.json()

    def fetch_group_list(self, jurisdiction: int, institution: int, page: int = 1) -> dict:
        """Fetch the list of groups where the children study.

        jurisdiction and institutions ids can be taken from fetch_children_List result
        ('.data.items[0].educations[0]')
        """
        path = '/api/journal/group/related-group-list'
        params = {
            'p_page': page,
            'p_jurisdictions[]': jurisdiction,
            'p_institutions[]': institution,
        }
        return self._fetch_json_for_path(path, params=params)

    def fetch_period_list(self, group: int, page=1) -> dict:
        """Fetch education periods for the given group.

        group can be taken from fetch_group_list result
        """
        path = '/api/group/group/get-list-period'
        params = {
            'p_group_ids[]': group,
            'p_page': page,
        }
        return self._fetch_json_for_path(path, params=params)

    def fetch_marks_for_period(self, education: int, date_from: Union[str, dt.date], date_to: Union[str, dt.date],
                               limit: int = 200, page: int = 1) -> dict:
        path = '/api/journal/estimate/table'
        if isinstance(date_from, dt.date):
            date_from = date_to_str(date_from)
        if isinstance(date_to, dt.date):
            date_to = date_to_str(date_to)

        params = {
            'p_educations[]': education,
            'p_date_from': date_from,
            'p_date_to': date_to,
            'p_limit': limit,
            'p_page': page
        }
        return self._fetch_json_for_path(path, params=params)

    def fetch_marks_for_current_quarter(self, education: int = 0, child_idx: int = 0) -> dict:
        if not education:
            children = self.fetch_children_list()
            assert child_idx < len(children['data']['items']), len(children['data']['items'])
            education = children['data']['items'][child_idx]['educations'][0]['education_id']
        today = dt.date.today()
        if today.month >= 9:
            q2_start = dt.date(today.year, 11, 4)
            if today < q2_start:
                q_start = dt.date(today.year, 9, 1)
                q_end = dt.date(today.year, 10, 24)
            else:
                q_start = q2_start
                q_end = dt.date(today.year, 12, 27)
        else:
            q4_start = dt.date(today.year, 4, 3)
            if today < q4_start:
                q_start = dt.date(today.year, 1, 10)
                q_end = dt.date(today.year, 3, 22)
            else:
                q_start = q4_start
                q_end = dt.date(today.year, 5, 30)
        return self.fetch_marks_for_period(education, q_start, q_end)
