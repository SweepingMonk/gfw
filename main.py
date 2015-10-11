#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import base64
import cStringIO

GFW_LIST_LINK="https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt"

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
            line = line.strip("\n")
            if line.startswith("||"):
                output.write(server_template.format(domain=line[2:], relay_dns=relay_dns))
                output.write(ipset_template.format(domain=line[2:], ipset_name=ipset_name))
            

def main():
    gfw_list = get_gfw_list()
    generate_dnsmasq_conf(gfw_list)

    gfw_list.close()


if __name__ == "__main__":
    main()

