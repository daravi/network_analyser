'''
e.g. python packet_drops.py -r nABRs/Device/ConnectionIssue/1810-2070795/
'''
import re
import argparse

import logging

import file_parser as fp
import re_patterns as patterns

logging.basicConfig(level=logging.WARNING)


parser = argparse.ArgumentParser()
parser.add_argument(
    "-r", "--root", help="Root directory of logs.", default=".")

args = parser.parse_args()
root = args.root

# root = "nABRs/Device/ConnectionIssue/1810-2070795/"
logs = fp.get_matched_files("Daemon Root", root)
devconn_files = fp.get_matched_files("devconn", root)
devices = fp.read_devconn(devconn_files)

# TODO differentiate between packetdrop (connection issue) and metadata drop (buffering issue - OoO)
packet_drop_counts = fp.get_count("packet_drop", logs, devices=devices)

total_drops = packet_drop_counts.sum()
print("-------------------------------------------------------")
for mac, count in packet_drop_counts.iteritems():
    name = devices.loc[mac]["name"]
    mfr = devices.loc[mac]["mfr"]
    model = devices.loc[mac]["model"]
    descriptor = "{0} ({1} - {2})".format(name, mfr, model)[0:30]
    print("| {0:<30} | {1:<7} | {2:4.1f}% |".format(
        descriptor, count, count*1.0/total_drops*100))
print("-------------------------------------------------------")
