#!/usr/bin/env python3.5
"""

Tag your instance and/or volumes with:
   Snapshot: yes|Yes|YES|1|true|True|TRUE|enable|Enabled|ENABLED

You can also pass instance ID or snapshot ALL (default).

It uses boto just like ansible, and you don't need to specify
credentials. You can use multiple boto profiles as described here:

http://boto.cloudhackers.com/en/latest/boto_config_tut.html

Arguments:
  ALL arguments are optional.
  -v VERBOSE mode
  -h help
  -i <instance id or list of ids>
  -p <boto profile>, default: default
  -n <1..1000>, default: 10, number of snapshots to keep for each volume
  -l <1..1000>, default: 24, number of hours that will elapse before creating a new snapshot


Examples:
  python snapshot_instances.py
       This will snapshot all volumes of all instances, keeping 10 snapshots
       creating a new one every day

  python snapshot_instances.py -i i-342abc3
       This will snapshot all volumes of i-342abc3, keeping 10 snapshots
       creating a new one every day

  python snapshot_instances.py -i i-342abc3,i-342abc4,i-213abc2
       This will snapshot all volumes of i-342abc3, keeping 10 snapshots
       creating a new one every day

  python snapshot_instances.py -p work -n 4 -l 168
       Snapshot all instances in your work profile, creating one snapshot
       per week, for 4 weeks

  python snapshot_instances.py -v
       Same as the first example, printing status as it goes.
"""

import sys
from datetime import timedelta
import datetime
import getopt
# import pdb
import boto
import dateutil.parser
from dateutil import tz

BOTO_PROFILE = 'default'
NUMBER_SNAPSHOTS = 10
LIFETIME = 24
TAG = ''
# LIFETIME is the number of hours minimum to create a new snapshot
# defaults to 1 per day

INSTANCE_IDS = ''
AWS_CONN = None
VERBOSE = False


def parse_args(argv):
    """
    Basic arg parsing
    """

    global BOTO_PROFILE, NUMBER_SNAPSHOTS, LIFETIME, INSTANCE_IDS, VERBOSE, TAG
    try:
        opts, args = getopt.getopt(argv, "t:p:n:l:i:vh")
    except getopt.GetoptError:
        print("Error parsing options")
        help()
        sys.exit(1)

    for opt, arg in opts:
        if opt == '-p':
            BOTO_PROFILE = arg
        elif opt == 't':
            TAG = arg
        elif opt == '-h':
            help()
            sys.exit(0)
        elif opt == '-v':
            VERBOSE = True
        elif opt == '-n':
            try:
                NUMBER_SNAPSHOTS = int(arg)
                if NUMBER_SNAPSHOTS < 1 or NUMBER_SNAPSHOTS > 1000:
                    NUMBER_SNAPSHOTS = 10
                    raise ValueError("Incorrect number of snapshots")
            except:
                print("Incorrect number of snapshots, using default %s" %
                      NUMBER_SNAPSHOTS)
        elif opt == '-l':
            try:
                LIFETIME = int(arg)
                if LIFETIME < 1 or LIFETIME > 1000:
                    LIFETIME = 24
                    raise ValueError("Incorrect LIFETIME(-l) value")
            except:
                print("Invalid -l argument, using default %s" % LIFETIME)
        elif opt == '-i':
            if arg.index(','):
                INSTANCE_IDS = arg.split(',')
            else:
                INSTANCE_IDS = [arg]
        else:
            print("Bad option: %s" % opt)


# def traverse_instances():
#    global conn, INSTANCE_IDS
#    reservations = conn.get_all_reservations()
#    for r in reservations:
#        for i in r.instances:
#            if i.id in INSTANCE_IDS:
#                INSTANCE_IDS.remove(i.id)
#                traverse_all_volumes_for_instance(i)
#    if len(INSTANCE_IDS) > 0:
#        print("\nError: the following instance ids where NOT found: %s" %
#              INSTANCE_IDS)

def traverse_instances():
    global conn, INSTANCE_IDS, TAG
    reservations = conn.get_all_reservations()
    for r in reservations:
        for i in r.instances:
            if i.id in INSTANCE_IDS:
                INSTANCE_IDS.remove(i.id)
                traverse_all_volumes_for_instance(i)
            if TAG != '':
                for tag in i.get_all_tags():
                    if tag.name == TAG:
                        if tag.value in ["1", "yes", "Yes", "YES", "enable", "Enable", "ENABLE"]:
                            traverse_all_volumes_for_instance(i)
    if len(INSTANCE_IDS) > 0:
        print("\nError: the following instance ids where NOT found: %s" %
              INSTANCE_IDS)


def traverse_all_instances():
    global conn
    reservations = conn.get_all_reservations()
    for r in reservations:
        for i in r.instances:
            traverse_all_volumes_for_instance(i)


def traverse_all_volumes():
    global conn, VERBOSE
#    if VERBOSE:
#        if 'Name' in instance_obj.tags:
#            print("Instance: %s, Name: %s" %
#                  (instance_obj.id, instance_obj.tags['Name']))
#        else:
#            print("Instance: %s" % instance_obj.id)
    volumes = conn.get_all_volumes(filters={'tag:Snapshot': ['yes', 'Yes']})
    for v in volumes:
        check_n_snapshot_volume(v)


def traverse_all_volumes_for_instance(instance_obj):
    global conn, VERBOSE
    if VERBOSE:
        if 'Name' in instance_obj.tags:
            print("Instance: %s, Name: %s" %
                  (instance_obj.id, instance_obj.tags['Name']))
        else:
            print("Instance: %s" % instance_obj.id)
    volumes = conn.get_all_volumes(
        filters={'attachment.instance-id': instance_obj.id})
    for v in volumes:
        check_n_snapshot_volume(v)


def check_n_snapshot_volume(volume_obj):
    global conn, NUMBER_SNAPSHOTS, VERBOSE
    if VERBOSE:
        if 'Name' in volume_obj.tags:
            print(" Volume: %s, Name: %s" %
                  (volume_obj.id, volume_obj.tags['Name']))
        else:
            print(" Volume: %s" % volume_obj.id)

            # first delete snapshots if necessary
    snapshots = volume_obj.snapshots()
    ordered_snaps = sorted(snapshots,
                           key=lambda vol: vol.start_time, reverse=True)
    if len(snapshots) >= NUMBER_SNAPSHOTS:
        while (len(ordered_snaps) >= NUMBER_SNAPSHOTS):
            del_snap = ordered_snaps.pop()
            print("  Deleting snapshot: %s, description: %s" % (
                del_snap.id, del_snap.description))
            del_snap.delete()

    now = datetime.datetime.now(tz.tzlocal())
    clock = now - timedelta(hours=LIFETIME)

    # create a snapshot if time is righ
    if len(ordered_snaps) > 0:
        newest = ordered_snaps.pop(0)
        start_time = dateutil.parser.parse(newest.start_time)

        if start_time < clock:
            snapshot_volume(volume_obj)
        elif VERBOSE:
            print("  Recent snapshot found: %s, %s" %
                  (newest.id, newest.description))
            # create snapshot if the instance doesn't have one
    else:
        snapshot_volume(volume_obj)


def snapshot_volume(volume_obj):
    now = datetime.datetime.now()
    desc = volume_obj.id + now.strftime("_%Y-%m-%d")
    print("  Creating snapshot %s" % desc)
    volume_obj.create_snapshot(desc)


def help():
    global NUMBER_SNAPSHOTS, LIFETIME, BOTO_PROFILE
    print("""
Use:
  -n <number of snapshots to keep, default %s>
  -l <number of hours each snapshot is going to be created, default %s>
  -t <TagName>, default 'Snapshot'
  -p <boto profile, default: '%s'>
  -i <instance id or list of ids, default: all instances are considered>
  -v VERBOSE mode
""" % (NUMBER_SNAPSHOTS, LIFETIME, BOTO_PROFILE))


if __name__ == "__main__":
    parse_args(sys.argv[1:])
    instances = 'all'
    if type(INSTANCE_IDS) is list:
        instances = str(INSTANCE_IDS)
    if VERBOSE:
        print("""Using boto profile: %s
Number of snapshots to keep for each volume: %s
Number of hours before creating a new snapshot: %s
Instances to consider: %s
""" % (BOTO_PROFILE, NUMBER_SNAPSHOTS, LIFETIME, instances))

    conn = boto.connect_ec2(profile_name=BOTO_PROFILE)
    if len(INSTANCE_IDS) > 0:
        traverse_instances()
    else:
        traverse_all_instances()
        traverse_all_volumes()
