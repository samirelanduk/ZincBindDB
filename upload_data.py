import subprocess
import os
import sys

# What is the site name?
if len(sys.argv) < 2:
    print("What is the site name?")
    sys.exit()
sitename = sys.argv[1]

# Upload data
subprocess.call(
 "scp -r data/* {}:~/{}/data/".format(sitename, sitename), shell=True
)
