from django.core import management
import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "csvimport.tests.settings")
if __name__ == "__main__":
    management.execute_from_command_line(sys.argv)
