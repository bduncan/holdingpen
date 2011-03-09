#!/usr/bin/env python

from distutils.core import setup
import os
import sys
import shutil
import errno

if sys.argv[1] == 'install':
    try:
        os.mkdir("scripts")
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise
    shutil.copyfile("debian/holdingpen.init", "scripts/holdingpen")
elif sys.argv[1] == 'clean':
    try:
        os.unlink("scripts/holdingpen")
        os.rmdir("scripts")
    except Exception:
        pass

setup(name="holdingpen",
      version="0.1",
      scripts=["holdingpen", "gatekeeper"],
      py_modules=["daemon"],
      data_files=[('/etc', ['holdingpen.conf']),
                  ('/etc/init.d', ['scripts/holdingpen']),
                  ('/usr/share/doc/holdingpen', ['README.md'])],
      author="Bruce Duncan",
      author_email="Bruce.Duncan@ed.ac.uk",
      url="https://github.com/bduncan/holdingpen"
      )
