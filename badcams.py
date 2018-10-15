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

# root = "nabr/1810-2070795/"
# logs = fp.get_matched_files("Daemon Root", root=root)
devconn_files = fp.get_matched_files("devconn", root=root)

devices = fp.read_devconn(devconn_files)
# packet_drop_counts = fp.get_packet_drop_counts(logs, devices)

# ip_pattern = re.compile(patterns.general["ip"])
# badcams = {}
# for file_name in daemon_log_files:
#     with open(file_name, 'r', encoding='utf-8') as infile:
#         log_obj["pattern"]

#         for line in infile:
#             if line[119:141] == "Metadata items dropped":
#                 mac = line[82:94]
#                 badcams.setdefault(mac, 0)
#                 badcams[mac] += 1
#             elif line[39:52] == "MissingPacket":
#                 # print(line)
#                 m = re.search(ip_pattern, line)
#                 # TODO: better regex to grab UDP vs TCP and port number
#                 if (m):
#                     ip = m.string[m.start():m.end()-1]
#                     # print("looking up mac for ip: {0}".format(ip))
#                     mac = cam_ip_lookup[ip]
#                     badcams.setdefault(mac, 0)
#                     badcams[mac] += 1
#                 else:
#                     print(line)


packet_drop_counts = {'00188520ae17': 92216, '0018851a19c4': 1821, '001885010853': 219, '00188500f927': 80, '0018851a14c2': 1249, '0018851a2496': 201, '00188513a8c5': 45, '0018851a5bd3': 31, '00188502a425': 105,
                      '00188500f928': 115, '00188500f76e': 215, '0018850100ef': 163, '00188506aad8': 113, '00188500f923': 135, '0018850100e3': 109, '0018850d2533': 32, '0018850628db': 65, '00188500be2c': 50, '00188500fb9f': 50}

total_drops = sum(packet_drop_counts.values())
print("-------------------------------------------------------")
for mac, drop_count in packet_drop_counts.items():
    name = devices[mac]["name"]
    mfr = devices[mac]["mfr"]
    model = devices[mac]["model"]
    descriptor = "{0} ({1} - {2})".format(name, mfr, model)[0:30]
    print("| {0:<30} | {1:<7} | {2:4.1f}% |".format(
        descriptor, drop_count, drop_count*1.0/total_drops*100))
print("-------------------------------------------------------")
# '{:<30}'.format('left aligned')
