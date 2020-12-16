#!/usr/bin/env python3
import json
import pickle

import pip._vendor.requests as requests

SESSION_PATH = 'dnevnik.session.pkl'
HEADERS_PATH = 'headers.json'


def main():
    with open(HEADERS_PATH) as f1:
        headers = json.load(f1)

    session = requests.Session()
    for header in headers:
        session.headers[header['name']] = header['value']

    with open(SESSION_PATH, 'wb') as f1:
        pickle.dump(session, f1)

if __name__ == '__main__':
    main()
