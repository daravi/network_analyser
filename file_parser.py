#!/usr/bin/python3
import xml.etree.ElementTree as ET
import collections
import csv
import fileinput
import os
import re
import sys as sys
from logging import info, warning, error, critical
from fnmatch import fnmatch as file_name_match

import pandas as pd

import re_patterns as patterns

# definitions
HTTP = 1
HTTPS = 2
RTP = 66


def get_matched_files(file_type, root="."):
    """
    Starting from root, walks down file tree and compares file names with input type
    Args:
        file_type (string): File type to match
        root (string): root directory to start search. Defaults to "." (optional)

    Returns:
        list: list of matched files
    """
    matched_files = {}

    pattern = re.compile(patterns.files[file_type])

    for (directory_path, directory_names, file_names) in os.walk(root):
        for file_name in file_names:
            if pattern.fullmatch(file_name):
                matched_files.setdefault(os.path.abspath(
                    directory_path), []).append(file_name)

    # For now we do not analyse multiple servers separately
    # We flatten all found file lists into the same list

    # for path in matched_files:
    #     print("Found {0} {1} files in {2}".format(len(path), file_type, path))

    # return matched_files

    matched_files_all = []
    for path, files in matched_files.items():
        info("Found {0} {1} files in {2}".format(len(files), file_type, path))
        for file in files:
            matched_files_all.append(path + "/" + file)

    return matched_files_all

# dr_files_list = sorted(dr_files_list, key=lambda s: int(s[85:-4]))


def read_fcp(file_list, fcp_type=""):
    """
    ...
    Args:
        file_list (list): ...
        fcp_type (string): ... (optional)

    Returns:
        DataFrame: ...
    """
    cpu_usage, mem_usage = pd.DataFrame(), pd.DataFrame()

    print("Reading {0} Fcp files".format(fcp_type))

    for file_name in file_list:
        # print("Reading {0}".format(file_name))
        cpu_column_names = ["Date", "CPU Sys", "CPU Proc"]
        mem_column_names = ["Date", "Mem Work", "Mem Virt"]
        with open(file_name) as f:
            column_count = next(f).count(",") + 1
            # print(column_count)
        if column_count == 12:
            cpu_columns, mem_columns = [0, 5, 6], [0, 10, 11]
        else:
            cpu_columns, mem_columns = [0, 6, 7], [0, 11, 12]

        cpu_fcp_df = pd.read_csv(
            file_name, usecols=cpu_columns, parse_dates=True,
            skipinitialspace=True, names=cpu_column_names,
            infer_datetime_format=True, index_col=0, dtype=str)

        mem_fcp_df = pd.read_csv(
            file_name, usecols=mem_columns, parse_dates=True,
            skipinitialspace=True, names=mem_column_names,
            infer_datetime_format=True, index_col=0, dtype=str)

        cpu_usage = cpu_usage.append(cpu_fcp_df, ignore_index=False)
        mem_usage = mem_usage.append(mem_fcp_df, ignore_index=False)

    # print("THIS IS MEM: ", mem_usage['Mem Work'])
    cpu_usage, mem_usage = cpu_usage.sort_index(), mem_usage.sort_index()

    # filter out non-valid cpu usage rows
    cpu_sys_re = re.compile(patterns.fcp["CPU Sys"])
    cpu_proc_re = re.compile(patterns.fcp["CPU Proc"])
    non_valid_rows = []
    for date, (cpu_sys, cpu_proc) in cpu_usage.iterrows():
        if not (bool(cpu_sys_re.fullmatch(cpu_sys)) and
                bool(cpu_proc_re.fullmatch(cpu_proc))):
            non_valid_rows.append(date)
    cpu_usage.drop(non_valid_rows, inplace=True)

    # filter out non-valid memory usage rows
    mem_work_re = re.compile(patterns.fcp["Mem Work"])
    mem_virt_re = re.compile(patterns.fcp["Mem Virt"])
    non_valid_rows = []
    for row in mem_usage.iterrows():
        date, (mem_work, mem_virt) = row
        if not (bool(mem_work_re.fullmatch(mem_work)) and
                bool(mem_virt_re.fullmatch(mem_virt))):
            non_valid_rows.append(date)
    mem_usage.drop(non_valid_rows, inplace=True)

    # print(cpu_usage, mem_usage)

    # convert usage data to usable units
    try:
        cpu_usage['CPU Sys'] = cpu_usage['CPU Sys'].str.rstrip('%').astype(int)
        cpu_usage['CPU Proc'] = cpu_usage['CPU Proc'].str.rstrip(
            '%').astype(int)
        mem_usage['Mem Work'] = mem_usage['Mem Work'].astype(int) / 1000
        mem_usage['Mem Virt'] = mem_usage['Mem Virt'].astype(int) / 1000
    except Exception as e:
        error_msg = "Issue parsing {0} fcp. Type: {1}, Arguments:\n{2!r}"
        print(error_msg.format(fcp_type, type(e).__name__, e.args))

    print("{0} Fcp files have ".format(fcp_type), len(cpu_usage), "CPU lines")
    print("{0} Fcp files have ".format(fcp_type), len(mem_usage), "MEM lines")

    return cpu_usage, mem_usage


def read_daemon_root(file_list):
    # create a DataFrame for "regular" log lines
    cols = ['type', 'module', 'message']
    dr = pd.DataFrame(columns=cols)
    p = re.compile(patterns.daemon["time"])
    sep = re.compile(patterns.daemon["sep"])
    # read all files
    with fileinput.input(file_list) as files:
        for line in files:
            m = p.match(line)
            if m:
                a = 2
                # matched time-stamp
                ts = pd.to_datetime(m.group(0))
                # rest of line
                data = sep.split(m.string[m.end():].strip())
                # # make sure data is the same length as cols
                data = data[:len(cols)] + [""]*(len(cols)-len(data))
                row = pd.DataFrame([data], columns=cols, index=[ts])
                dr = dr.append(row, ignore_index=False)
            else:
                # analyse non-regular log lines
                pass
    return dr

# dr=read_daemon_root(fl)

# noinspection PyShadowingNames


def read_daemon_root_pd(file_list1):
    """
        Reads the Daemon Root files uses the entry from get_matched_files("Daemon Fcp")
        :return: file_daemon_pd
    """
    file_daemon_pd = pd.DataFrame()
    labels = ['date', 'event', 'do not know', 'content']
    for fname in file_list1:
        if 'Analytics' not in str(fname) and 'Daemon.Root' in str(fname):
            with fileinput.input(fname) as file1:
                with open('log.csv', 'w') as outfile:
                    csv_file = csv.writer(outfile)
                    csv_file.writerow(labels)
                    # will test for date at the beginning of the line
                    ss = re.compile('\d\d\d\d')

                    for line in file1:
                        line1 = ''.join(line.strip())
                        lpr = ss.match(line1.split('-')[0])
                        if lpr:
                            if 'Fcp' not in line1:
                                line1 = line1.split(' : ')
                                line0 = line1[0].split(' ')
                                line_data = str(line1[1:])
                                try:
                                    if len(line1) > 1:
                                        line2 = (
                                            line0[0] + ' ' + line0[1] + ',' + line0[2] + ',' + line_data)
                                        line2 = line2.split(',')
                                        csv_file.writerow(line2)
                                    else:
                                        line2 = (
                                            line0[0] + ' ' + line0[1] + ',' + line0[2])
                                        # line2 = str(','.join(line2))
                                        line2 = line2.split(',')
                                        csv_file.writerow(line2)
                                except Exception as e:
                                    print(len(line1))
                                    print("Error: ", e)

    file_read = pd.read_csv('log.csv', names=labels, usecols=[
                            0, 1, 2, 3], parse_dates=[0], index_col=0)
    file_daemon_pd = file_daemon_pd.append(file_read, ignore_index=False)
    return file_daemon_pd


# def read_daemon_root(file_list1):
#     """
#         Reads the Daemon Root files uses the entry from get_matched_files("Daemon Fcp")
#         :return: file_daemon_pd
#     """
#     i = 1
#     global file_daemon

#     flist2 = [fname for fname in file_list1 if 'Analytics' not in str(fname) and 'Daemon.Root' in str(fname)]
#     with fileinput.input(flist2) as file3:
#         file_daemon = [line5 for line5 in file3 if line5 not in ['Fcp']]
#         i += 1
#     # print('lines', file_daemon)
#     return file_daemon


# noinspection PyShadowingNames
def read_client_root_pd(file_list1):
    """
        Reads the Client Root files uses the entry from get_client_fcp_file_list
        :return: file_client_pd
    """
    file_client_pd = pd.DataFrame()
    labels = ['date', 'event', 'do not know', 'content']
    for fname in file_list1:
        if 'Analytics' not in str(fname) and 'Client.Root' in str(fname):
            with fileinput.input(fname) as file1:
                with open('log.csv', 'w') as outfile:
                    csv_file = csv.writer(outfile)
                    csv_file.writerow(labels)
                    # will test for date at the beginning of the line
                    ss = re.compile('\d\d\d\d')

                    for line in file1:
                        line1 = ''.join(line.strip())
                        lpr = ss.match(line1.split('-')[0])
                        if lpr:
                            if 'Fcp' not in line1:
                                line1 = line1.split(' : ')
                                line0 = line1[0].split(' ')
                                line_data = str(line1[1:])
                                try:
                                    if len(line1) > 1:
                                        line2 = (
                                            line0[0] + ' ' + line0[1] + ',' + line0[2] + ',' + line_data)
                                        line2 = line2.split(',')
                                        csv_file.writerow(line2)
                                    else:
                                        line2 = (
                                            line0[0] + ' ' + line0[1] + ',' + line0[2])
                                        # line2 = str(','.join(line2))
                                        line2 = line2.split(',')
                                        csv_file.writerow(line2)
                                except Exception as e:
                                    print(len(line1))
                                    print("Error: ", e)

    file_read = pd.read_csv('log.csv', names=labels, usecols=[
                            0, 1, 2, 3], parse_dates=[0], index_col=0)
    file_client_pd = file_client_pd.append(file_read, ignore_index=True)
    return file_client_pd


def read_devconn(file_list):
    devices = {}
    # process all devconn files:
    mac_pattern = re.compile(patterns.general["mac"])
    for file_name in file_list:
        if os.stat(file_name).st_size == 0:
            continue
        tree = ET.parse(file_name)
        root = tree.getroot()
        # process all device entries in each file
        for device_connection in root.iter("DeviceConnection"):
            # read device mac address:
            device_id = device_connection.find("DeviceId").text.lower()
            m_mac = re.search(mac_pattern, device_id)
            if m_mac:
                mac = m_mac.string[m_mac.start():m_mac.end()].replace(":", "")
            else:
                mac = device_connection.find(
                    "PhysicalAddress").text.lower().replace(":", "")
            # read connection type (http or https)
            protocol_type_tag = device_connection.find("ProtocolType")
            # read device ip
            ip_found = False
            if (protocol_type_tag):
                # return the main ip address for device
                for app_endpoint in device_connection.iter("AppEndpoint"):
                    proto_type = int(app_endpoint.find("ProtoType").text)
                    if (proto_type==int(protocol_type_tag.text)):
                        ip = app_endpoint.find("Address").text
                        connection_type = ("Encrypted" if (proto_type == HTTPS) else "Not Encrypted")
                        ip_found = True
                        break
            else:
                # return the http or https ip address for device
                for app_endpoint in device_connection.iter("AppEndpoint"):
                    proto_type = int(app_endpoint.find("ProtoType").text)
                    if proto_type in [HTTP, HTTPS]:
                        ip = app_endpoint.find("Address").text
                        connection_type = ("Encrypted" if (proto_type == HTTPS) else "Not Encrypted")
                        ip_found = True
                        break
            if not ip_found:
                # return first ip address for device
                ip = next(device_connection.iter("AppEndpoint")).find("Address").text
            # read device info
            mfr_tag = device_connection.find("MfrString")
            mfr = mfr_tag.find("Mfr").text
            model = mfr_tag.find("Model").text
            serial = mfr_tag.find("Serial").text
            user_tag = device_connection.find("UserStrings")
            name = user_tag.find("Name").text
            location = user_tag.find("Location").text
            devices[mac] = {"ip": ip, "mac": mac, "connection_type": connection_type,
                            "mfr": mfr, "model": model, "serial": serial,
                            "name": name, "location": location}
    pd_devices = pd.DataFrame.from_dict(devices, orient='index')
    return pd_devices


def get_packet_drop_counts(file_list, devices):
    """ network connection issue """
    # TODO: break down this function to multiple smaller parts
    # TODO: return a pandas DataFrame instead of a dictionary
    def trim_id(log_id, id_raw):
        if log_id == "mac":
            return id_raw.replace(":", "").lower()
        else:
            return id_raw.lower()
    drop_counts = {}
    with fileinput.input(file_list) as files:
        for line in files:
            # TODO differentiate between packetdrop (connection issue) and metadata drop (buffering issue - OoO)
            # check against all log objects that indicate network packet
            for log_obj in patterns.log_types["packet_drop"]:
                log_pattern = log_obj["pattern"]
                # check if log line indicates packet drop
                m_log = re.search(log_pattern, line)
                if m_log:
                    # get mac
                    mac_found = False
                    log_id = log_obj["id"]
                    id_pos = log_obj["id_pos"]
                    m_id = re.findall(patterns.general[log_id], line.lower())
                    if len(m_id) >= id_pos+1:
                        id_raw = m_id[id_pos][0]
                        id = trim_id(log_id, id_raw)
                    else:
                        warning(
                            "Could not read device identifier of type \"{0}\" at position {1} for log line:\n{2}\n".format(log_id, id_pos, line))
                        continue
                    # find mac from the device identifier
                    for device_mac, info in devices.iterrows():
                        if info[log_id]==id:
                            mac = device_mac
                            mac_found = True
                            break     
                    if mac_found:
                        # increment drop count
                        drop_counts.setdefault(mac, 0)
                        drop_counts[mac] += 1
                    else:
                        # get_mac(devices, line, log_obj)
                        # TODO: figure out what is 0.0.0.0 for e.g.
                        # 2018-10-05 07:00:21 WARN  : ? : RTP RX MissingPacket(s) 1 on RtpOverRtsp:0/1/SSRC:1717395308(665d5f6c) from 0.0.0.0/SSRC:3543483746(d3354562) / Thread IoService.TransportCtrl [logNum 74]
                        if (id!="0.0.0.0"):
                            warning("Could not find mac address for device with \"{0}\"={1} for log line:\n{2}\n".format(log_id, id, line))
                    # TODO: better regex to grab UDP vs TCP and port number
                    break
    pd.DataFrame()
    return drop_counts



def filter_device(logs, mac, filename=""):
    if filename=="":
        filename = os.path.join(os.getcwd(), "device_" + mac + "log")
    with fileinput.input(file_list) as files:
        for line in files:
            if 

# def get_mac(devices, line, log_obj):
#     def trim_id(log_id, id_raw):
#         if log_id == "mac":
#             return id_raw.replace(":", "").lower()
#         else:
#             return id_raw.lower()
#     mac_found = False
#     log_id = log_obj["id"]
#     id_pos = log_obj["id_pos"]
#     m_id = re.findall(patterns.general[log_id], line.lower())
#     if len(m_id) >= id_pos+1:
#         id_raw = m_id[id_pos][0]
#         id = trim_id(log_id, id_raw)
#     return None
