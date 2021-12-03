import argparse
import json
from pathlib import Path

from dnevnik2 import Dnevnik2


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('cookies_path')
    args = arg_parser.parse_args()

    cookies_path = Path(args.cookies_path).expanduser()
    dnevnik = Dnevnik2.make_from_cookies_file(cookies_path)
    children = dnevnik.fetch_children_list()
    text = json.dumps(children, indent=2, ensure_ascii=False)
    print(text)


if __name__ == '__main__':
    main()
