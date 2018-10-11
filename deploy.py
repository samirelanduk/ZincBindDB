import subprocess
import os
import sys

# What is the site name?
if len(sys.argv) < 2:
    print("What is the site name?")
    sys.exit()
sitename = sys.argv[1]

if len(sys.argv) < 3 or sys.argv[2] != "nofiles":
    # Remove contents of remote source directory
    subprocess.call(
     "ssh {} 'rm -r ~/{}/source/* >& /dev/null'".format(sitename, sitename), shell=True
    )

    # What files are being tracked by git?
    tracked_files = subprocess.check_output("git ls-files", shell=True).decode()
    tracked_files = list(filter(bool, tracked_files.split("\n")))

    # Push source code to remote
    commands = []
    for file_ in tracked_files:
        directory = "/".join(file_.split("/")[:-1])
        commands.append("mkdir -p ~/{}/source/{}".format(sitename, directory))
    commands = set(commands)
    subprocess.call(
     "ssh {} '{}'".format(sitename, ";".join(commands)), shell=True
    )
    files = []
    for file_ in tracked_files:
        subprocess.call(
         "scp -r ./{} {}:~/{}/source/{}".format(file_, sitename, sitename, file_), shell=True
        )

# Turn off Debug
subprocess.call(
 "ssh {} 'sed -i s/\"DEBUG = True\"/\"DEBUG = False\"/g ~/{}/source/core/settings.py'".format(sitename, sitename),
 shell=True
)

# Add allowed hosts
subprocess.call(
 "ssh {} 'sed -i s/\"ALLOWED_HOSTS = \[\]\"/\"ALLOWED_HOSTS = \[£'{}£'\]\"/g ~/{}/source/core/settings.py'".format(sitename, sitename, sitename, sitename),
 shell=True
)
subprocess.call(
 "ssh {} 'sed -i s/£/\\\"/g ~/{}/source/core/settings.py'".format(sitename, sitename),
 shell=True
)

# Add google analytics
subprocess.call(
 "ssh {} 'sed -i s/\"<!--analytics-->\"/\"\{{% include \\\"analytics.html\\\" %\}}\"/g ~/{}/source/core/templates/base.html'".format(sitename, sitename),
 shell=True
)

# Make data go above source
subprocess.call(
 "ssh {} 'sed -i s/data/..\\\/data/g ~/{}/source/core/settings.py'".format(sitename, sitename),
 shell=True
)
subprocess.call(
 "ssh {} 'sed -i s/data\\\//..\\\/data\\\//g ~/{}/source/core/models.py'".format(sitename, sitename),
 shell=True
)
subprocess.call(
 "ssh {} 'sed -i s/data\\\//..\\\/data\\\//g ~/{}/source/core/views.py'".format(sitename, sitename),
 shell=True
)

# Install pip packages
subprocess.call(
 "ssh {} '~/{}/env/bin/pip install -r ~/{}/source/requirements.txt -r ~/{}/source/requirements-live.txt'".format(sitename, sitename, sitename, sitename),
 shell=True
)

# Apply migrations
subprocess.call(
 "ssh {} '~/{}/env/bin/python ~/{}/source/manage.py migrate'".format(sitename, sitename, sitename),
 shell=True
)

# Deploy static files
subprocess.call(
 "ssh {} 'cd ~/{}/source && ../env/bin/python manage.py compilescss'".format(sitename, sitename),
 shell=True
)
subprocess.call(
 "ssh {} 'cd ~/{}/source && ../env/bin/python manage.py collectstatic --noinput'".format(sitename, sitename),
 shell=True
)
