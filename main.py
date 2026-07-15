import configparser

from RecieptPrinter import RecieptPrinter
from tasks_printer.context import build_context
from tasks_printer.printer import render_receipt


def main():
    config = configparser.ConfigParser()
    config.read("config.ini")

    context = build_context(config)
    p = RecieptPrinter(dry=False)
    render_receipt(p, context, config)


if __name__ == "__main__":
    main()
