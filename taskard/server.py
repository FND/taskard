import argparse
import os
import sys

from taskard.config import ConfigurationError
from taskard.logging import configure_sql_logging


def main():
    parser = argparse.ArgumentParser(description="launch Taskard server")
    parser.add_argument("--mode",
            help="set configuration mode (takes precedence over "
                    "TASKARD_CONFIG envionment variable)")
    parser.add_argument("--dev", action="store_true",
            help="activate development mode - short for `--mode=development`")
    parser.add_argument("-p", "--port", nargs="?", default="5000",
            help="specify the port number to listen on (defaults to 5000)")
    args = parser.parse_args()

    # NB: configuration mode must be set before application is imported
    if args.dev:
        os.environ["TASKARD_CONFIG"] = "development"
    elif args.mode:
        os.environ["TASKARD_CONFIG"] = args.mode

    try:
        from taskard.web import app
    except ConfigurationError as err:
        print("ERROR: %s" % err, file=sys.stderr)
        return False

    if args.dev:
        configure_sql_logging()

    print(" * Starting up in %s mode" % app.config_mode)
    app.run(port=int(args.port))
    return True


if __name__ == "__main__":
    status = not main()
    sys.exit(status)
