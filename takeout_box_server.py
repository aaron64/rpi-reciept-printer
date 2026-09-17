import argparse
import configparser

from RecieptPrinter import RecieptPrinter
from takeout_box_printer.server import create_app


def load_config():
    config = configparser.ConfigParser(interpolation=None)
    config.read("config.ini")
    return config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true", help="Print to console only, skip the physical printer")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()

    config = load_config()
    server_config = config["TakeoutBoxServer"] if "TakeoutBoxServer" in config else {}

    host = args.host or server_config.get("host", "0.0.0.0")
    port = args.port or int(server_config.get("port", "8080"))
    auth_token = server_config.get("auth_token", "")

    p = RecieptPrinter(dry=args.dry)
    app = create_app(p, auth_token)
    app.run(host=host, port=port, threaded=False)


if __name__ == "__main__":
    main()
