# good_feeder

Dumps and colorizes Jenkins RSS feeds.

## Usage

```
usage: good_feeder [-h] [-a AUTH] [-L] [--insecure] [--html] [-S SEP] [-l] [-f] [-s [SEARCH]] [-n] [-V] [jenkins_url]

good_feeder v{vesion_here}

positional arguments:
  jenkins_url           URL to server, folder, or job

optional arguments:
  -h, --help            show this help message and exit
  -a AUTH, --auth AUTH  Format: "username:token" (or omit "-a" and use JENKINS_AUTH environment variable)
  -L, --localtime       Convert server UTC timestamp to local time
  --insecure            Disable SSL certificate verification
  --html                Output as html (i.e. email)
  -S SEP, --sep SEP     default string: '»', max length: 2
  -l, --latest          Show only latest builds
  -f, --failed          Show only failed builds
  -s [SEARCH], --search [SEARCH]
                        Filter output on sub-string (case-sensitive)
  -n, --negate          Negate search filter
  -V, --version         Show version
```

## Example

```sh
# Anonymous query
good_feeder https://my_jenkins_host

# Authenticated query (via argument)
good_feeder -a "myUser:myPassword" https://my_jenkins_host

# Authenticated query (via environment)
JENKINS_AUTH="myUser:myPassword"
export JENKINS_AUTH
good_feeder https://my_jenkins_host
```
