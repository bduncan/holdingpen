#!/usr/bin/env python
# vim: fileencoding=utf-8:

import os
import sys
import socket
import ConfigParser
import subprocess
import atexit


def cleanup(sock):
    sock.close()


def main():
    defaults = {"socket": "/var/run/holdingpen.socket"}
    config = ConfigParser.SafeConfigParser(defaults)
    config.read('/etc/holdingpen.conf')
    sock = socket.socket(socket.AF_UNIX)
    sock.connect(config.get("main", "socket"))
    os.execvp(sys.argv[0], sys.argv[1:] or [''])
    #atexit.register(cleanup, sock)
    # close_fds is the default, but since we rely on it strongly, make it
    # explicit.
    #subprocess.Popen(sys.argv, close_fds=False)

if __name__ == '__main__':
    main()
