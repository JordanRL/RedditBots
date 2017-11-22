import os
import subprocess
import signal
from pprint import pprint

proc = subprocess.Popen(["pgrep", 'run.py'], stdout=subprocess.PIPE)

for pid in proc.stdout:
    pprint(vars(pid))
