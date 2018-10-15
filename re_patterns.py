files = {
    "Daemon Root": r"^Daemon\.Root(\.(\d|10))?(\.(\d|10))?\.log$",
    "Daemon Device": r"^Daemon\.Device(\.(\d|10))?(\.(\d|10))?\.log$",
    "Daemon Fcp": r"^Daemon\.Fcp(\.(\d|10))?(\.(\d|10))?\.csv$",
    "Daemon Exception": r"^Daemon\.Exception(\.(\d|10))?(\.(\d|10))?\.log$",
    "Client Root": r"^Client\.Root(\.(\d|10))?(\.(\d|10))?\.log$",
    "Client Fcp": r"^Client\.Fcp(\.(\d|10))?(\.(\d|10))?\.csv$",
    "Client Exception": r"^Client\.Exception(\.(\d|10))?(\.(\d|10))?\.log$",
    "devconn": r"[A-Z]_Avigilon_DeviceConnections_devconn\.cfg$",
}

fcp = {
    "CPU Sys": r"^(\d|\d\d|100)%$",
    "CPU Proc": r"^(\d|\d\d|100)%$",
    "Mem Work": r"^\d*$",
    "Mem Virt": r"^\d*$",
}

daemon = {
    "time": r"^((?P<date>\d\d\d\d-(0[1-9]|1(1|2))-(0[1-9]|(1|2)\d|3(0|1))) (?P<time>((0|1)\d|2[0-4]):([0-5]\d):([0-5]\d)))",
    "sep": r" +: +",
}

# note - the ip regex depends on regex group parsing to be from left to right in order to work correctly
general = {
    "ip": r"((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9]))",
    "mac": r"(((\d|[a-f]){12})|(((\d|[a-f]){2}:){5}(\d|[a-f]){2}))",
}

log_types = {
    "packet_drop": [{"pattern": r"Metadata items dropped", "id": "mac", "id_pos": 0, "desc": "Overloaded network port"},
                    {"pattern": r"MissingPacket",          "id": "ip",  "id_pos": 0, "desc": "Unreliable link"}],
    "db_corruption": [],
}

# "time": r"^\d\d\d\d-(0[1-9]|1(1|2))-(0[1-9]|(1|2)\d|3(0|1)) ((0|1)\d|2[0-4]):([0-5]\d):([0-5]\d)$",
