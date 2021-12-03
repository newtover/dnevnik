import argparse
import getpass
import sys
from pathlib import Path

import dnevnik2


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('cookies_path')
    args = arg_parser.parse_args()

    cookies_path = Path(args.cookies_path).expanduser()

    email = input(f'Email for {dnevnik2.BASE_URL}: ')
    password = getpass.getpass()

    dnevnik = dnevnik2.Dnevnik2.make_from_login_by_email(email, password)
    dnevnik.save_cookies(cookies_path)

    print(f'Saved cookies into {args.cookies_path}', file=sys.stderr)


if __name__ == '__main__':
    main()
