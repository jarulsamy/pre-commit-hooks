import argparse
import sys
from datetime import datetime

import yaml
from fuzzywuzzy import fuzz


class UserConfig:
    def __init__(self, filename):
        # self.names = []
        # self.types = []
        # self.sections = []
        self.config = {}
        self.load(filename)

    def load(self, filename):
        with open(filename, "r") as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        if "Date" in self.config:
            self.config["Date"] = datetime.now().strftime("%m/%d/%Y")


def valid_date(date_text):
    try:
        datetime.strptime(date_text, "%m/%d/%Y")
        return True
    except ValueError:
        return False


def valid_percent_format(text, formats):
    for format_ in formats:
        if "%" not in format_:
            continue

        elif fuzz.partial_ratio(text, format_) > 65:
            num = [int(s) for s in text.split() if s.isdigit()]
            if len(num) != 1:
                return False
            num = num[0]

            try:
                format_ % num
            except TypeError:
                return False
            else:
                return True

    return False


def check_header(f, config: list):
    # first_four_lines = []
    SUCCESS = []
    WARNING = []
    FAIL = []

    for k, v in config.config.items():
        line = f.readline().strip()
        if line not in v:
            if valid_date(line):
                WARNING.append(k)
            elif not valid_percent_format(line, v):
                FAIL.append(k)
        else:
            SUCCESS.append(k)

    if len(FAIL) > 0:
        return 1, [SUCCESS, WARNING, FAIL]
    return 0, [SUCCESS, WARNING, FAIL]


def main(argv=None):
    retv = 0

    parser = argparse.ArgumentParser("Fixes the headers of files",)
    parser.add_argument("filenames", nargs="*", help="Filenames to fix")
    parser.add_argument(
        "-c",
        "--config",
        help="Path to config file",
        required=False,
        default=".header.yaml",
    )
    args = parser.parse_args(argv)

    config = UserConfig(args.config)
    for filename in args.filenames:
        with open(filename, "r") as f:
            file_ret, results = check_header(f, config)
            retv |= file_ret
            if file_ret:
                print(
                    f"{filename}: {len(results[2])} Error(s), {len(results[1])} Warning(s)."
                )
                if len(results[2]) > 0:
                    print("Errors:")
                    for i in results[2]:
                        print(f"\t{i}")
                print()
                if len(results[1]) > 0:
                    print("Warnings:")
                    for i in results[2]:
                        print(f"\t{i}")
    return retv


if __name__ == "__main__":
    sys.exit(main())
