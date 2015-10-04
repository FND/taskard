import argparse
import os
import sys

from taskard.logging import configure_sql_logging


def main():
    parser = argparse.ArgumentParser(description="launch Taskard server")
    parser.add_argument("--mode",
            help="set configuration mode (takes precedence over TASKARD_ENV "
                    "envionment variable)")
    parser.add_argument("--dev", action="store_true",
            help="activate development mode - short for `--mode=development`")
    parser.add_argument("-p", "--port", nargs="?", default="5000",
            help="specify the port number to listen on (defaults to 5000)")
    args = parser.parse_args()

    # NB: configuration mode must be set before application is imported
    if args.dev:
        os.environ["TASKARD_ENV"] = "development"
    elif args.mode:
        os.environ["TASKARD_ENV"] = args.mode

    from taskard.web import app

    if args.dev:

        configure_sql_logging(app)

    print(" * Starting up in %s mode" % app.config_mode)
    app.run(port=int(args.port))
    return True


if __name__ == "__main__":
    status = not main()
    sys.exit(status)
