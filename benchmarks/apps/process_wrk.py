import re
from typing import Any, Dict


def wrk_csv_cols() -> str:
    return """Latency average [ms],Latency stdev [ms],Latency max[ms],Requests average,Requests stdev,Requests max,Total requests,Total duration,read,err_connect,err_read,err_write,err_timeout,Req/Sec,Transfer/sec [MB/s]"""


def wrk_data(wrk_output: Dict[str, Any]) -> str:
    return (
        str(wrk_output.get("lat_avg"))
        + ","
        + str(wrk_output.get("lat_stdev"))
        + ","
        + str(wrk_output.get("lat_max"))
        + ","
        + str(wrk_output.get("req_avg"))
        + ","
        + str(wrk_output.get("req_stdev"))
        + ","
        + str(wrk_output.get("req_max"))
        + ","
        + str(wrk_output.get("tot_requests"))
        + ","
        + str(wrk_output.get("tot_duration"))
        + ","
        + str(wrk_output.get("read"))
        + ","
        + str(wrk_output.get("err_connect"))
        + ","
        + str(wrk_output.get("err_read"))
        + ","
        + str(wrk_output.get("err_write"))
        + ","
        + str(wrk_output.get("err_timeout"))
        + ","
        + str(wrk_output.get("req_sec_tot"))
        + ","
        + str(wrk_output.get("transfer_sec"))
    )


def get_mib(size_str: str) -> Any:
    x = re.search("^(\d+\.*\d*)(\w+)$", size_str)
    if x is not None:
        size = float(x.group(1))
        suffix = (x.group(2)).lower()
    else:
        return size_str

    if suffix == "b":
        return size / (1024 ** 2)
    elif suffix == "kb" or suffix == "kib":
        return size / (1024)
    elif suffix == "mb" or suffix == "mib":
        return size
    elif suffix == "gb" or suffix == "gib":
        return size * 1024
    elif suffix == "tb" or suffix == "tib":
        return size * 1024 ** 2
    elif suffix == "pb" or suffix == "pib":
        return size * 1024 ** 3

    return False


def get_number(number_str: str) -> Any:
    x = re.search("^(\d+\.*\d*)(\w*)$", number_str)
    if x is not None:
        size = float(x.group(1))
        suffix = (x.group(2)).lower()
    else:
        return number_str

    if suffix == "k":
        return size * 1000
    elif suffix == "m":
        return size * 1000 ** 2
    elif suffix == "g":
        return size * 1000 ** 3
    elif suffix == "t":
        return size * 1000 ** 4
    elif suffix == "p":
        return size * 1000 ** 5
    else:
        return size

    return False


def get_ms(time_str: str) -> Any:
    x = re.search("^(\d+\.*\d*)(\w*)$", time_str)
    if x is not None:
        size = float(x.group(1))
        suffix = (x.group(2)).lower()
    else:
        return time_str

    if suffix == "us":
        return size / 1000
    elif suffix == "ms":
        return size
    elif suffix == "s":
        return size * 1000
    elif suffix == "m":
        return size * 1000 * 60
    elif suffix == "h":
        return size * 1000 * 60 * 60
    else:
        return size

    return False


def parse_wrk_output(wrk_output: str) -> Dict[str, Any]:
    retval = {}
    for line in wrk_output.splitlines():
        x = re.search(
            "^\s+Latency\s+(\d+\.\d+\w*)\s+(\d+\.\d+\w*)\s+(\d+\.\d+\w*).*$", line
        )
        if x is not None:
            retval["lat_avg(ms)"] = get_ms(x.group(1))
            retval["lat_stdev(ms)"] = get_ms(x.group(2))
            retval["lat_max(ms)"] = get_ms(x.group(3))
        x = re.search(
            "^\s+Req/Sec\s+(\d+\.\d+\w*)\s+(\d+\.\d+\w*)\s+(\d+\.\d+\w*).*$", line
        )
        if x is not None:
            retval["req_avg"] = get_number(x.group(1))
            retval["req_stdev"] = get_number(x.group(2))
            retval["req_max"] = get_number(x.group(3))
        x = re.search(
            "^\s+(\d+)\ requests in (\d+\.\d+\w*)\,\ (\d+\.\d+\w*)\ read.*$", line
        )
        if x is not None:
            retval["tot_requests"] = get_number(x.group(1))
            retval["tot_duration"] = get_ms(x.group(2))
            retval["read"] = get_mib(x.group(3))
        x = re.search("^Requests\/sec\:\s+(\d+\.*\d*).*$", line)
        if x is not None:
            retval["req_sec_tot"] = get_number(x.group(1))
        x = re.search("^Transfer\/sec\:\s+(\d+\.*\d*\w+).*$", line)
        if x is not None:
            retval["transfer_sec"] = get_mib(x.group(1))
        x = re.search(
            "^\s+Socket errors:\ connect (\d+\w*)\,\ read (\d+\w*)\,\ write\ (\d+\w*)\,\ timeout\ (\d+\w*).*$",
            line,
        )
        if x is not None:
            retval["err_connect"] = get_number(x.group(1))
            retval["err_read"] = get_number(x.group(2))
            retval["err_write"] = get_number(x.group(3))
            retval["err_timeout"] = get_number(x.group(4))
    if "err_connect" not in retval:
        retval["err_connect"] = 0
    if "err_read" not in retval:
        retval["err_read"] = 0
    if "err_write" not in retval:
        retval["err_write"] = 0
    if "err_timeout" not in retval:
        retval["err_timeout"] = 0
    return retval
