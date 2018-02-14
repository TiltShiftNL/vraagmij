import subprocess
from django.template import Library

register = Library()

try:
    head = subprocess.Popen("ls -al /.dockerenv",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    VERSION = [l.strip() for l in head.stdout.readlines()]
except:
    VERSION = u'unknown'


@register.simple_tag()
def git_short_version():
    print(len(VERSION))
    return VERSION