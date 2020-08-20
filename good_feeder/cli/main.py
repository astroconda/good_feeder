#!/usr/bin/env python
import os
import colorama
import feedparser
import pytz
import tzlocal
import urllib3
import requests
import sys
from datetime import datetime
from .. import __version__


DEFAULT_DEPTH_SEPARATOR = chr(0xbb)
DEPTH_SEPARATOR = DEFAULT_DEPTH_SEPARATOR
DEPTH_SEPARATOR_MAXLEN = 2
TZ = tzlocal.get_localzone()


def auth_valid(s):
    if ":" in s:
        return True
    return False


def auth_split(s):
    return s.split(":", 1)


def separator_apply(delim, s):
    return s.replace(DEFAULT_DEPTH_SEPARATOR, delim)


def main():
    import argparse
    parser = argparse.ArgumentParser(
            description=f"{os.path.basename(sys.argv[0])} v{__version__}")

    parser.add_argument('-a', '--auth',
                        help='Format: "username:token" (or omit "-a"'
                        ' and use JENKINS_AUTH environment variable)',
                        type=str)

    parser.add_argument('-L', '--localtime',
                        help='Convert server UTC timestamp to local time',
                        action='store_true')

    parser.add_argument('--insecure',
                        help='Disable SSL certificate verification',
                        action='store_true')

    parser.add_argument('--html',
                        help='Output as html (i.e. email)',
                        action='store_true')

    parser.add_argument('-S', '--sep',
                        help=f"default string: '{DEFAULT_DEPTH_SEPARATOR}', "
                            f"max length: {DEPTH_SEPARATOR_MAXLEN}",
                        action='store',
                        type=str)

    parser.add_argument('-l', '--latest',
                        help="Show only latest builds",
                        action='store_true')

    parser.add_argument('-f', '--failed',
                        help="Show only failed builds",
                        action='store_true')

    parser.add_argument('-s', '--search',
                        help='Filter output on sub-string (case-sensitive)',
                        action='append',
                        nargs="?",
                        type=str)

    parser.add_argument('-n', '--negate',
                        help='Negate search filter',
                        action='store_true')

    parser.add_argument('-V', '--version',
                        help='Show version',
                        action='store_true')

    parser.add_argument('jenkins_url',
                        help='URL to server, folder, or job',
                        nargs='?',
                        type=str)

    args = parser.parse_args()
    username = ""
    token = ""

    if args.version:
        print(__version__)
        return 0

    if not args.jenkins_url:
        parser.print_help()
        print("\nJenkins URL required\n", file=sys.stderr)
        return 1

    # Disable SSL drivel when in insecure mode
    if args.insecure:
        urllib3.disable_warnings()

    # Consume authentication string argument, or via environment (not both)
    # i.e. username:token
    if args.auth:
        if not auth_valid(args.auth):
            print("Invalid auth string", file=sys.stderr)
            return 1
        username, token = auth_split(args.auth)
    elif os.environ.get("JENKINS_AUTH"):
        if not auth_valid(os.environ["JENKINS_AUTH"]):
            print("Invalid JENKINS_AUTH string", file=sys.stderr)
            return 1
        username, token = auth_split(os.environ["JENKINS_AUTH"])

    # Set default server entrypoint
    if args.failed:
        jenkins_url = f"{args.jenkins_url}/rssFailed"
    elif args.latest:
        jenkins_url = f"{args.jenkins_url}/rssLatest"
    else:
        jenkins_url = f"{args.jenkins_url}/rssAll"

    # Is this an anonymous or authenticated server query?
    if not username and not token:
        auth_data = None
    else:
        auth_data = (username, token)

    if args.sep:
        DEPTH_SEPARATOR = args.sep
        if len(DEPTH_SEPARATOR) > DEPTH_SEPARATOR_MAXLEN:
            DEPTH_SEPARATOR = DEPTH_SEPARATOR[:DEPTH_SEPARATOR_MAXLEN]

    # Get RSS data
    data = requests.get(jenkins_url, auth=auth_data, verify=not args.insecure)

    # On failure dump whatever Jenkins needs you to know (RAW HTML)
    if not data:
        print(data.text, file=sys.stderr)
        return 1

    # Consume RSS feed data
    feed = feedparser.parse(data.text)

    if args.html:
        color_date = "black"
    else:
        color_date = colorama.Fore.BLUE

    # Verify we have data to iterate over
    if not feed or not feed.entries:
        print("No records")
        return 0

    # Begin dumping RSS records
    for rec in feed.entries:
        if args.html:
            color_title = "red"
        else:
            color_title = colorama.Fore.RED

        if '(stable)' in rec.title or '(back to normal)' in rec.title:
            if args.html:
                color_title = "green"
            else:
                color_title = colorama.Fore.GREEN

        if args.localtime:
            dt = datetime.strptime(rec.published, "%Y-%m-%dT%H:%M:%SZ")
            rec.published = dt.replace(tzinfo=pytz.utc)\
                    .astimezone(TZ)\
                    .strftime("%Y-%m-%dT%H:%M:%S")

        if args.html:
            output_fmt = \
                f"<span style=\"color:{color_date}\">{rec.published}</span>: "\
                f"<span style=\"color:{color_title}\">{rec.title}</span> "\
                f"(<a href=\"{rec.link}\">link</a>)<br>"
        else:
            output_fmt = \
                f"{color_date}{rec.published}{colorama.Style.RESET_ALL}: "\
                f"{color_title}{rec.title}{colorama.Style.RESET_ALL} "\
                f"({rec.link})"

        # Apply user-defined separator
        if args.sep:
            output_fmt = separator_apply(DEPTH_SEPARATOR, output_fmt)

        # User-defined search is additive (-s str1 -s str2 -s str...)
        if args.search:
            for pattern in args.search:
                if args.negate:
                    # Negated search
                    if pattern not in rec.title:
                        print(output_fmt)
                else:
                    # Normal search
                    if pattern in rec.title:
                        print(output_fmt)
        else:
            print(output_fmt)


if __name__ == '__main__':
    sys.exit(main)
