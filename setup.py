#!/usr/bin/env python

from distutils.core import setup

setup(name="holdingpen",
      version="0.1",
      scripts=["holdingpen", "gatekeeper"],
      py_modules=["daemon"],
      data_files=[('/etc/init.d', ['init.d/holdingpen'])],
      author="Bruce Duncan",
      author_email="Bruce.Duncan@ed.ac.uk",
      url="https://github.com/bduncan/holdingpen"
      )
