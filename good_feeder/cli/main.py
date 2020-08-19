#!/usr/bin/env python
import os
import colorama
import feedparser
import urllib3
import requests
import sys
from pprint import pprint
from .. import __version__

def auth_valid(s):
    if ":" in s:
        return True
    return False

def auth_split(s):
    return s.split(":", 1)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--auth', help='Format: "username:token" (or omit "-a" and use JENKINS_AUTH environment variable)', type=str)
    parser.add_argument('--insecure', help='Disable SSL certificate verification', action='store_true')
    parser.add_argument('-l', '--latest', help="Show only latest builds", action='store_true')
    parser.add_argument('-f', '--failed', help="Show only failed builds", action='store_true')
    parser.add_argument('-s', '--search', help='Filter output on sub-string (case-sensitive)', action='append', nargs="?", type=str)
    parser.add_argument('-n', '--negate', help='Negate search filter', action='store_true')
    parser.add_argument('--html', help='Output as html (i.e. email)', action='store_true')

    parser.add_argument('-V', '--version', help='Show version', action='store_true');
    parser.add_argument('jenkins_url', type=str, nargs='?')
    args = parser.parse_args()

    username = ""
    token = ""

    if args.version:
        print(__version__)
        exit(0)

    if not args.jenkins_url:
        print("Jenkins URL required (i.e. https://jenkins OR https://jenkins/job/folder")
        exit(1)

    # Disable SSL drivel when in insecure mode
    if args.insecure:
        urllib3.disable_warnings()

    # Consume authentication string argument, or via environment (not both)
    # i.e. username:token
    if args.auth:
        if not auth_valid(args.auth):
            print("Invalid auth string")
            exit(1)
        username, token = auth_split(args.auth)
    elif os.environ.get("JENKINS_AUTH"):
        if not auth_valid(os.environ["JENKINS_AUTH"]):
            print("Invalid JENKINS_AUTH string")
            exit(1)
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
        auth_data=None
    else:
        auth_data = (username, token)

    # Get RSS data
    data = requests.get(jenkins_url, auth=auth_data, verify=not args.insecure)

    # On failure dump whatever Jenkins needs you to know (RAW HTML)
    if not data:
        print(data.text, file=sys.stderr)
        exit(1)


    # Consume RSS feed data
    feed = feedparser.parse(data.text)

    if args.html:
        color_date = "black"
    else:
        color_date = colorama.Fore.BLUE

    # Verify we have data to iterate over
    if not feed or not feed.entries:
        print("No records")
        exit(0)

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

        if args.html:
            output_fmt = f"<span style=\"color:{color_date}\">{rec.published}</span>: " \
                f"<span style=\"color:{color_title}\">{rec.title}</span> " \
                f"(<a href=\"{rec.link}\">link</a>)<br>"
        else:
            output_fmt = f"{color_date}{rec.published}{colorama.Style.RESET_ALL}: " \
                f"{color_title}{rec.title}{colorama.Style.RESET_ALL} " \
                f"({rec.link})"

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
