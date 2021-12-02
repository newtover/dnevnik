import requests

from pprint import pprint as pp

import datetime

js = {
    "activation_code": None,
    "login": "LOGIN",
    "password": "PASSWORD",
    "type": "email",
    "_isEmpty": False,
}

session = requests.Session()

session.post("https://dnevnik2.petersburgedu.ru/api/user/auth/login", json=js)
users = session.get("https://dnevnik2.petersburgedu.ru/api/journal/person/related-child-list").json()

pp(users)

if len(users["data"]["items"]) == 1:
    ed_id = users["data"]["items"][0]["educations"][0]["education_id"]
    group_id = users["data"]["items"][0]["educations"][0]["group_id"]
else:
    # user = int(input("Введите пользователя"))
    user = 0 # 0 - первый пользователь(хотя список users может содержать и больше)
    ed_id = users["data"]["items"][user]["educations"][0]["education_id"]
    group_id = users["data"]["items"][user]["educations"][0]["group_id"]

params = {
    "p_groups[]": group_id,
    "p_education[]": ed_id,
    "p_educations[]": ed_id,
    "p_datetime_from": str(datetime.datetime.today() - datetime.timedelta(days=14)),
    "p_datetime_to": str(datetime.datetime.today()),
    "p_limit": 200,
    "p_page": 1,
}

marks = session.get("https://dnevnik2.petersburgedu.ru/api/journal/estimate/table", params=params).json()
pp(marks)

