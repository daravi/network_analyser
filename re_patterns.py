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


log_components = {
    "date": r"(?P<date>(\d\d\d\d-(0[1-9]|1(1|2))-(0[1-9]|(1|2)\d|3(0|1))))",
    "time": r"(?P<time>(((0|1)\d|2[0-4]):([0-5]\d):([0-5]\d)))",
    "level": r"(?P<level>(INFO|WARN|ERROR|FATAL))",
    "function": r"(?P<function>(\S+))",
    "message": r"(?P<message>(\S+))",
}

date = r"(?P<date>(\d\d\d\d-(0[1-9]|1(1|2))-(0[1-9]|(1|2)\d|3(0|1))))"
time = r"(?P<time>(((0|1)\d|2[0-4]):([0-5]\d):([0-5]\d)))"
level = r"(?P<level>(INFO|WARN|ERROR|FATAL))"
function = log_components["function"]
dr_message = log_components["message"]
# DL 1.00188520ae17: (t201:CameraApp:3.24.2.74:24553) [2141719(480) 2018-10-11T12:35:55.155Z] Sys/src/Sys/StreamManagerVideoH4.cpp:4642 "Restarting pipeline..."
# DL 1.0018851a14c2: (t204:CameraApp:3.2.0.44:20890) [1709250(75) 2018-05-18T12:00:52.826Z] Net/src/Net/NetworkManager.cpp:1851 "Starting NTP service"
# DL 1.00188502a425: (t001:CameraApp:4.4.0.2:2029) [173093(4049) 17669d:12h:01m:14s] /Rtp/RtpSession.cpp:879 "StreamRxRtp attached to peer source SSRC:2425498718(90922c5e)"
model_id = r"(?P<model_id>([\w|\d]+))"
fw_name = r"(?P<fw_name>([\w]+))"
fw_version = r"(?P<fw_version>([\d|.]+))"
build_number = r"(?P<build_number>([\d]+))"
fw_id = r"(?P<fw_id>({0}:{1}:{2}:{3}))".format(
    model_id, fw_name, fw_version, build_number)
dd_message = r"(DL 1.{0}: \({1}\) )"

logs = {
    "Daemon Root": [
        {
            "pattern": r"(^{0} {1} {2} : {3} : {4}$)".format(date, time, level, function, dr_message),
            "description": "General Daemon Root log line",
        },
        {
            "pattern": r"(^{0} {1} {2} : {3} : {4}$)".format(date, time, level, function, missing_packet),
            "description": "A video packet delivery failed.",
        },
        {
            "pattern": r"(^{0} {1} {2} : {3} : {4}$)".format(date, time, level, function, metadata_dropped),
            "description": "A metadata packet delivery failed.",
        }
    ],
    "Daemon Device": [
        {
            "pattern": r"(^{0} {1} {2} : {3} : {4}$)".format(date, time, level, function, dd_message),
            "description": "General Daemon Root log line",
        },
        {},
    ]
}

# daemon = {
#     "timestampt": r"^{0} {1} {2} : {3} : {4}$".format(date, time, level, function, message),
#     "time": r"^((?P<date>\d\d\d\d-(0[1-9]|1(1|2))-(0[1-9]|(1|2)\d|3(0|1))) (?P<time>((0|1)\d|2[0-4]):([0-5]\d):([0-5]\d)))",
#     "sep": r" +: +",
# }

# note - the ip regex depends on regex group parsing to be from left to right in order to work correctly
general = {
    "ip": r"((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9]))",
    "mac": r"(((\d|[a-f]){12})|(((\d|[a-f]){2}:){5}(\d|[a-f]){2}))",
}

issues = {
    "packet_drop": [{"re": r"Metadata items dropped", "id": "mac", "id_pos": 0, "desc": "Overloaded network port"},
                    {"re": r"MissingPacket",          "id": "ip",  "id_pos": 0, "desc": "Unreliable link"}],
    "db_corruption": [],
}

# "time": r"^\d\d\d\d-(0[1-9]|1(1|2))-(0[1-9]|(1|2)\d|3(0|1)) ((0|1)\d|2[0-4]):([0-5]\d):([0-5]\d)$",


logs = {
    "Daemon Root": [{"pattern": ^ date_time: $a: $b$, "description": ""}.
                    {},
                    {}]
}
