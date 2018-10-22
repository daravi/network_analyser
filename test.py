# [173093(4049)
import file_parser as fp
logs = fp.get_matched_files("Daemon Device", ".")
with fileinput.input(logs) as files:
    for line in files:
