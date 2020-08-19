# good_feeder

Dumps and colorizes Jenkins RSS feeds.

## Usage

```
usage: good_feeder [-h] [-a AUTH] [--insecure] [-l] [-f] [-s [SEARCH]] [-n] [--html] [-V] [jenkins_url]

positional arguments:
  jenkins_url

optional arguments:
  -h, --help            show this help message and exit
  -a AUTH, --auth AUTH  Format: "username:token" (or omit "-a" and use JENKINS_AUTH environment variable)
  --insecure            Disable SSL certificate verification
  -l, --latest          Show only latest builds
  -f, --failed          Show only failed builds
  -s [SEARCH], --search [SEARCH]
                        Filter output on sub-string (case-sensitive)
  -n, --negate          Negate search filter
  --html                Output as html (i.e. email)
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
