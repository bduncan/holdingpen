#!/usr/bin/env python

from distutils.core import setup
from subprocess import Popen, PIPE
import os
import sys
import shutil
import errno


def git_describe(abbrev=4):
    p = Popen(['git', 'describe', '--abbrev=%d' % abbrev], stdout=PIPE)
    return p.communicate()[0].split('\n')[0].strip()


setup(name="holdingpen",
      version=git_describe(),
      scripts=["holdingpen", "gatekeeper"],
      py_modules=["daemon"],
      data_files=[('/etc', ['holdingpen.conf']),
                  ('/etc/init.d', ['scripts/holdingpen']),
                  ('/usr/share/doc/holdingpen', ['README.md'])],
      author="Bruce Duncan",
      author_email="Bruce.Duncan@ed.ac.uk",
      url="https://github.com/bduncan/holdingpen",
      license="GNU GPLv3",
      )
