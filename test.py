#!/usr/bin/env python

import subprocess
import os


if __name__ == '__main__':
    statusfile = "/proc/%d/status" % os.getpid()
    meminfo = subprocess.check_output(["grep", "Vm", statusfile]).split("\n")
    meminfo.remove("")
    meminfo = [mem.replace('\t', ' ') for mem in meminfo if "RSS" in mem or "Size" in mem]
    memreport = "\tMEM Usage: " + "\t".join(meminfo)
    print memreport
