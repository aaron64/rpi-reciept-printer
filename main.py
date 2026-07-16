import argparse
import configparser

from RecieptPrinter import RecieptPrinter
from tasks_printer.context import build_context
from tasks_printer.printer import render_receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true", help="Print to console only, skip the physical printer")
    args = parser.parse_args()

    config = configparser.ConfigParser(interpolation=None)
    config.read("config.ini")

    context = build_context(config)
    p = RecieptPrinter(dry=args.dry)
    render_receipt(p, context, config)


if __name__ == "__main__":
    main()
