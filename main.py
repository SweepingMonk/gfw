#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import base64
import cStringIO
import re
import urlparse

GFW_LIST_LINK="https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt"

DOMAIN = 1
PREFIX = 2
KEYWORDS = 3

def get_gfw_list():
    gfw_list = urllib2.urlopen(GFW_LIST_LINK).read()
    gfw_list = base64.standard_b64decode(gfw_list)

    with open("gfwlist.txt") as fp:
        gfw_list += fp.read()

    return cStringIO.StringIO(gfw_list)


def generate_dnsmasq_conf(gfw_list, file_name="gfw.conf",
                          relay_dns="127.0.0.1#1053", ipset_name="gfw"):
    server_template = "server=/.{domain}/{relay_dns}\n"
    ipset_template = "ipset=/.{domain}/{ipset_name}\n"

    with open("gfw.conf", "w") as output:
        for line in gfw_list:
            line = line.strip("\n").strip("/")
            if line.startswith("||"):
                output.write(server_template.format(domain=line[2:], relay_dns=relay_dns))
                output.write(ipset_template.format(domain=line[2:], ipset_name=ipset_name))


def parse(content):
    def match_line(line):
        if len(line) == 0 or line.startswith('!'):
            return 0, None

        if(line.startswith('||')):
            return DOMAIN, line[2:]

        if(line.startswith('|')):
            return PREFIX, line[1:]

        if(line.startswith('@@')):
            code, rule = match_line(line[2:])
            return -code, rule

        return KEYWORDS, line

    positive_rules, negative_rules = {}, {}
    for line in content:
        code, rule = match_line(line.strip())
        if code == 0:
            continue

        if code < 0:
            negative_rules.setdefault(abs(code), []).append(rule)
        else:
            positive_rules.setdefault(abs(code), []).append(rule)

    return positive_rules, negative_rules


def get_content_by_url(uri, decoder=None):
    parse_result = urlparse.urlparse(uri)

    if re.match('^https?$', parse_result.scheme):
        resp = urllib2.urlopen(uri)
        content = resp.read()
    elif parse_result.scheme == 'file':
        with open(parse_result.path) as fp:
            content = fp.read()
    else:
        raise ValueError('Unsupported Schema')

    if decoder:
        content = decoder(content)

    return cStringIO.StringIO(content)


def main():
    positive, negative = parse(get_content_by_url(GFW_LIST_LINK, base64.standard_b64decode))
    print positive[DOMAIN]
    print positive[PREFIX]
    print positive[KEYWORDS]

if __name__ == "__main__":
    main()
