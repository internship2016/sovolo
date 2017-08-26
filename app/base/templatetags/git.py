import subprocess
from django.template import Library

register = Library()

GIT_VERSION = None


@register.simple_tag()
def git_version():
    global GIT_VERSION

    if GIT_VERSION:
        return GIT_VERSION

    try:
        head = subprocess.Popen("git rev-parse --short HEAD",
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)

        GIT_VERSION = head.stdout.readline().strip()
    except:
        GIT_VERSION = 'unknown'

    return GIT_VERSION
