#!/usr/bin/env python
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
from django.core.management.commands.runserver import Command as runserver
runserver.default_port = "8050"
from django.core.management import execute_from_command_line
execute_from_command_line(sys.argv)
