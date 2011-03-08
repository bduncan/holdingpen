#!/usr/bin/env python
# vim: fileencoding=utf-8:

import os
import sys
import socket
import ConfigParser
import StringIO


def main():
    # Try to open the socket, but if not, we must still run the program.
    try:
        default = """[main]
socket = /var/run/holdingpen.socket
        """
        config = ConfigParser.SafeConfigParser()
        config.readfp(StringIO.StringIO(default))
        config.read('/etc/holdingpen.conf')
        sock = socket.socket(socket.AF_UNIX)
        sock.connect(config.get("main", "socket"))
    except Exception:
        pass
    # Pass the opened socket to the program. If the program decides to close
    # all descriptors, this will not work. An alternative will be fork and
    # pause for SIGCHLD before exiting.
    # Again, that won't work if the program forks and execs. An excessive
    # alternative in that case would be to use ptrace.
    # In any case, the socket should remain open as long as the program is
    # using the resource.
    os.execvp(sys.argv[1], sys.argv[1:])

if __name__ == '__main__':
    main()
