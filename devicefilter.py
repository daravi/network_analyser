import re
import argparse

import logging

import file_parser as fp
import re_patterns as patterns

import pandas as pd

logging.basicConfig(level=logging.WARNING)


parser = argparse.ArgumentParser()
parser.add_argument(
    "-r", "--root", help="Root directory of logs.", default=".")

args = parser.parse_args()
root = args.root

root = "nABRs/Device/DeviceFilter/1810-2070795/"
logs = fp.get_matched_files("Daemon Root", root=root)
devconn_files = fp.get_matched_files("devconn", root=root)

devices = pd.DataFrame(fp.read_devconn(devconn_files))
print(devices)
macs, ips = {}, {}
for mac, info in devices.iterrows():
	macs[mac] = info["ip"]
	ips[info["ip"]] = mac

mac = input('Please enter device mac: ') 
ip = ips[mac]
fp.filter_device(logs, mac)

print(macs)
print(ips)