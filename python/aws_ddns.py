#!/usr/bin/env python2
"""
 Author: jose@josehidalgo.net,
 github.com/joseche

 Requirements:
 pip install boto urlopen

 Credentials:
 You need to have your AWS keys in this file ~/.aws/credentials:
 [default]
 aws_access_key_id=<YOUR ACCESS KEY ID>
 aws_secret_access_key=<YOUR SECRET KEY>


TODO: make it a class
TODO: also accept region as argument
TODO: set either public ip or private ip


"""


import sys
import getopt
import traceback
import datetime
from json import load

#from urllib.request import urlopen
from urllib2 import urlopen

import boto.route53


VERBOSE = False


def verb(msg):
    """ wrapper """
    global VERBOSE
    if VERBOSE:
        print(msg)


def usage():
    print("""
Missing arguments, use -d <domain> -r <record_name>
optional:
   boto profile: -p <profile_name>
   VERBOSE: -v
""")
    sys.exit(1)


def main(argv):
    global VERBOSE
    profile = 'default'
    domain = None
    record = None
    rrset = None
    awsip = None
    conn = None

    try:
        opts, args = getopt.getopt(argv, "p:d:r:v", ["profile=", "domain=", "record="])
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt == '-p':
            profile = arg
        elif opt == '-d':
            domain = arg
        elif opt == '-r':
            record = arg
        elif opt == '-v':
            VERBOSE = True

    if (domain is None) or (record is None):
        usage()

    # sanity
    if domain[-1] != '.':
        domain = domain + '.'
    if record.count('.') < 1:
        record = record + '.' + domain

    verb('domain: ' + domain)
    verb('record: ' + record)
    if profile != 'default':
        verb('profile: ' + profile)

    curip = load(urlopen('http://httpbin.org/ip'))['origin']
    verb('Current public ip: ' + curip)

    try:
        # conn = boto.route53.connect_to_region('us-east-1', profile_name=profile)
        conn = boto.route53.connect_to_region('us-west-1', profile_name=profile)
        if conn:
            zone = conn.get_zone(domain)
            if zone:
                rrset = zone.get_a(record, False)
                if rrset:
                    awsip = rrset.to_print()
                    verb(record + ' is set to ' + awsip)
                    if awsip == curip:
                        print('Update not necessary')
                    else:
                        now = datetime.datetime.now()
                        print('Updating ' + record + ' to ' + curip + ' at ' + str(now))
                        status = zone.update_record(rrset, curip)
                        print(status)
                else:
                    print('Record: ' + record + ' not found!, check your zone')
            else:
                print('Zone ' + domain + ' not found')
        else:
            print('Unable to connect, check your boto credentials')

    except:
        print(traceback.format_exc(False))
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main(sys.argv[1:])

