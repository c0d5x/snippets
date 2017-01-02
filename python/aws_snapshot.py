#!/usr/bin/env python
"""
This script creates snapshots for all your instances or a set
of instances received as argument.

It uses boto just like ansible, and you don't need to specify
credentials. You can use multiple boto profiles as described here:

http://boto.cloudhackers.com/en/latest/boto_config_tut.html

Arguments:
  ALL arguments are optional.
  -v Verbose mode
  -h help
  -i <instance id or list of ids>
  -p <boto profile>, default: default
  -n <1..1000>, number of snapshots to keep for each volume
  -l <1..1000>, number of hours that will elapse before creating a new snapshot


Examples:
  python snapshot_instances.py
       This will snapshot all volumes of all instances, keeping 10 snapshots
       creating a new one every week

  python snapshot_instances.py -i i-342abc3
       This will snapshot all volumes of i-342abc3, keeping 10 snapshots
       creating a new one every week

  python snapshot_instances.py -i i-342abc3,i-342abc4,i-213abc2
       This will snapshot all volumes of i-342abc3, keeping 10 snapshots
       creating a new one every week

  python snapshot_instances.py -p work -n 4 -l 168
       Snapshot all instances in your work profile, creating one snapshot
       per week, for 4 weeks

  python snapshot_instances.py -v
       Same as the first example, printing status as it goes.
"""


import sys
import getopt
import datetime
from datetime import timedelta
import dateutil.parser
from dateutil import tz
import boto

SNAPS = 10
LIFETIME = 168.0


boto_profile = 'default'
number_snapshots = SNAPS
lifetime = LIFETIME
# lifetime is the number of hours minimum to create a new snapshot
# defaults to 1 week

instance_ids = ''
aws_conn = None
verbose = False


def parse_args(argv):
    global boto_profile, number_snapshots, lifetime, instance_ids, verbose
    try:
        opts, args = getopt.getopt(argv, "p:n:l:i:vh")
    except getopt.GetoptError:
        print("Error parsing options")
        help()
        sys.exit(1)

    for opt, arg in opts:
        if opt == '-p':
            boto_profile = arg
        elif opt == '-h':
            help()
            sys.exit(0)
        elif opt == '-v':
            verbose = True
        elif opt == '-n':
            try:
                number_snapshots = int(arg)
                if number_snapshots < 1 or number_snapshots > 1000:
                    number_snapshots = SNAPS
                    raise ValueError("Incorrect number of snapshots")
            except:
                print("Incorrect number of snapshots, using default %s" %
                      number_snapshots)
        elif opt == '-l':
            try:
                lifetime = int(arg)
                if lifetime < 1 or lifetime > 1000:
                    lifetime = LIFETIME
                    raise ValueError("Incorrect lifetime(-l) value")
            except:
                print("Invalid -l argument, using default %s" % lifetime)
        elif opt == '-i':
            if arg.index(','):
                instance_ids = arg.split(',')
            else:
                instance_ids = [arg]
        else:
            print("Bad option: %s" % opt)


def traverse_instances():
    global conn, instance_ids
    reservations = conn.get_all_reservations()
    for r in reservations:
        for i in r.instances:
            if i.id in instance_ids:
                instance_ids.remove(i.id)
                traverse_all_volumes(i)
    if len(instance_ids) > 0:
        print("\nError: the following instance ids where NOT found: %s" %
              instance_ids)


def traverse_all_instances():
    global conn
    reservations = conn.get_all_reservations()
    for r in reservations:
        for i in r.instances:
            traverse_all_volumes(i)


def traverse_all_volumes(instance_obj):
    global conn, verbose
    if verbose:
        if 'Name' in instance_obj.tags:
            print("Instance: %s, Name: %s" %
                  (instance_obj.id, instance_obj.tags['Name']))
        else:
            print("Instance: %s" % instance_obj.id)
    volumes = conn.get_all_volumes(
        filters={'attachment.instance-id': instance_obj.id})
    for v in volumes:
        check_volume(v)


def check_volume(volume_obj):
    global conn, number_snapshots, verbose
    if verbose:
        if 'Name' in volume_obj.tags:
            print(" Volume: %s, Name: %s" %
                  (volume_obj.id, volume_obj.tags['Name']))
        else:
            print(" Volume: %s" % volume_obj.id)

# first delete snapshots if necessary
    snapshots = volume_obj.snapshots()
    ordered_snaps = sorted(snapshots,
                           key=lambda vol: vol.start_time, reverse=True)
    if len(snapshots) >= number_snapshots:
        while (len(ordered_snaps) >= number_snapshots):
            del_snap = ordered_snaps.pop()
            print("  Deleting snapshot: %s, description: %s" % (
                  del_snap.id, del_snap.description))
            del_snap.delete()

    now = datetime.datetime.now(tz.tzlocal())
    clock = now - timedelta(hours=lifetime)

# create a snapshot if time is righ
    if len(ordered_snaps) > 0:
        newest = ordered_snaps.pop(0)
        start_time = dateutil.parser.parse(newest.start_time)

        if start_time < clock:
            snapshot_volume(volume_obj)
        elif verbose:
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
    global number_snapshots, lifetime, boto_profile
    print("""
Use:
  -n <number of snapshots to keep, default %s>
  -l <number of hours each snapshot is going to be created, default %s, %s days>
  -p <boto profile, default: '%s'>
  -i <instance id or list of ids, default: all instances are considered>
  -v verbose mode
""" % (number_snapshots, lifetime, (lifetime / 24.0), boto_profile))


if __name__ == "__main__":
    parse_args(sys.argv[1:])
    instances = 'all'
    if type(instance_ids) is list:
        instances = str(instance_ids)
    if verbose:
        print("""Using boto profile: %s
Number of snapshots to keep for each volume: %s
Number of hours before creating a new snapshot: %s, %s days
Instances to consider: %s
""" % (boto_profile, number_snapshots, lifetime, (lifetime / 24.0), instances))

    conn = boto.connect_ec2(profile_name=boto_profile)
    if len(instance_ids) > 0:
        traverse_instances()
    else:
        traverse_all_instances()
