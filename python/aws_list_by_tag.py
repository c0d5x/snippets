#!/usr/bin/env python3.5
"""
List EC2 instances and EBS volumes with a Tag

Arguments:
  -v VERBOSE mode
  -h help
  -p <boto profile>, default: ''
  -t <tag>

"""

import sys
import getopt
import boto
import boto.ec2
import dateutil.parser
from dateutil import tz

BOTO_PROFILE = ''
TAG = ''

AWS_CONN = None
VERBOSE = False


def parse_args(argv):
    """
    Basic arg parsing
    """

    global BOTO_PROFILE, VERBOSE, TAG
    try:
        opts, _ = getopt.getopt(argv, "t:p:vh")
    except getopt.GetoptError:
        print("Error parsing options")
        help()
        sys.exit(1)

    for opt, arg in opts:
        if opt == '-p':
            BOTO_PROFILE = arg
        elif opt == '-t':
            TAG = arg
        elif opt == '-h':
            help()
            sys.exit(0)
        elif opt == '-v':
            VERBOSE = True
        else:
            print("Bad option: %s" % opt)
    if TAG == '':
        help()
        sys.exit(0)



def traverse_all_instances_with_tag():
    global conn
    reservations = conn.get_all_reservations(filters={'tag:' + TAG: ['yes', 'Yes']})
    if len(reservations) > 0:
        print("Instances with tag:")
    for r in reservations:
        for i in r.instances:
            if 'Name' in i.tags:
                print("\t%s - %s" % (i.tags['Name'], i.id))
            else:
                print("\t%s" % i.id)


def traverse_all_volumes_with_tag():
    global conn, VERBOSE, TAG
    volumes = conn.get_all_volumes(filters={'tag:' + TAG: ['yes', 'Yes']})
    if len(volumes) > 0:
        print ("Volumes with tag:")
    for v in volumes:
        if 'Name' in v.tags:
            print("\t%s - %s" % (v.tags['Name'], v.id))
        else:
            print("\t%s" % v.id)



def help():
    global BOTO_PROFILE
    print("""
Use:
  -t <TagName>
  -p <boto profile, default: '%s'>
  -v VERBOSE mode
""" % (BOTO_PROFILE))


if __name__ == "__main__":
    parse_args(sys.argv[1:])
    if VERBOSE:
        print("""Using boto profile: %s
Tag: %s
""" % (BOTO_PROFILE, TAG))

    regions = ['us-east-1', 'us-west-1', 'us-west-2']
    for region in regions:
        print ("Checking region '%s':" % region)
        if len(BOTO_PROFILE) > 0:
            conn = boto.ec2.connect_to_region(region, profile_name=BOTO_PROFILE)
        else:
            conn = boto.ec2.connect_to_region(region)

        traverse_all_instances_with_tag()
        traverse_all_volumes_with_tag()
