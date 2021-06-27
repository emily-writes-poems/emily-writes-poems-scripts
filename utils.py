import sys


def error_exit(message):
    print("ERROR: " + message, file=sys.stderr)
    sys.exit(-1)
