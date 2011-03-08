#!/usr/bin/env python
# vim: fileencoding=utf-8:

import atexit
import os
import sys
import socket
import ConfigParser
import errno
import select
import logging
import StringIO
import mmap
from contextlib import closing


log = logging.getLogger("holdingpen")


class ResourceStack(object):
    def __init__(self, nblocks, blocksize):
        self._nblocks = nblocks
        self._blocksize = blocksize
        for i in range(self._nblocks):
            self.alloc()

    def finalise(self):
        for i in range(len(self)):
            self.free()


class MmapStack(ResourceStack):
    def __init__(self, *args, **kwargs):
        self._blocks = []
        super(MmapStack, self).__init__(*args, **kwargs)

    def alloc(self):
        if len(self._blocks) < self._nblocks:
            # 0x2000 is MAP_LOCKED
            self._blocks.append(mmap.mmap(-1, self._blocksize,
                mmap.MAP_PRIVATE | 0x2000))
            self._blocks[-1].write('\0' * self._blocksize)

    def free(self):
        if len(self._blocks) > 0:
            self._blocks[-1].close()
            del self._blocks[-1]

    def __len__(self):
        return len(self._blocks)


class FileStack(ResourceStack):
    def __init__(self, *args, **kwargs):
        try:
            os.mkdir("tmp")
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise
        self._i = 0
        super(FileStack, self).__init__(*args, **kwargs)

    def alloc(self):
        if self._i < self._nblocks:
            open("tmp/%d" % (self._i), "w").close()
            self._i += 1

    def free(self):
        if self._i > 0:
            self._i -= 1
            os.unlink("tmp/%d" % (self._i))

    def finalise(self):
        super(FileStack, self).finalise()
        os.rmdir("tmp")

    def __len__(self):
        return len(os.listdir("tmp"))


def main():
    default = """[main]
socket = /var/run/holdingpen.socket
mode = 448 ; 0700 in decimal
blocksize = 1048576 ; 1024 * 1024 = 1 MiB
blocks = 2
resource = Mmap
    """
    config = ConfigParser.SafeConfigParser()
    config.readfp(StringIO.StringIO(default))
    config.read('/etc/holdingpen.conf')
    open_sockets = []
    with closing(socket.socket(socket.AF_UNIX)) as listen_sock:
        # Unix sockets can't be reused. This seems to be how people handle it.
        os.unlink(config.get("main", "socket"))
        listen_sock.bind(config.get("main", "socket"))
        # Set permissions, if appropriate
        # fchmod and fchown don't work on sockets :(
        if config.has_option("main", "mode"):
            os.chmod(config.get("main", "socket"),
                     config.getint("main", "mode"))
        uid = config.has_option("main", "owner") and \
            config.getint("main", "owner") or -1
        gid = config.has_option("main", "group") and \
            config.getint("main", "group") or -1
        if uid >= 0 or gid >= 0:
            os.chown(config.get("main", "socket"), uid, gid)
        listen_sock.listen(5)
        log.debug("socket bound: %r", listen_sock)
        resclass = getattr(sys.modules['__main__'],
                           config.get("main", "resource") + "Stack")
        res = resclass(config.getint("main", "blocks"),
                       config.getint("main", "blocksize"))
        atexit.register(res.finalise)
        while True:
            # select without timeout
            log.debug("open_sockets: %r", open_sockets)
            r, w, x = select.select([listen_sock] + open_sockets, [], [])
            log.debug("select returned %r" % (r))
            for sock in r:
                if sock is listen_sock:
                    # Add the socket object to the list of open sockets.
                    open_sockets.append(listen_sock.accept()[0])
                    if len(res):
                        res.free()
                        log.info("Allocated a block to client on %r",
                            open_sockets[-1])
                    else:
                        log.warn("Ran out of blocks to allocate to client on %r",
                            open_sockets[-1])
                    continue
                data = r[0].recv(1024)
                if data:
                    log.warn("%r sent some data! Really just expected the"
                          + " socket to close... recv returned '%s'",
                          r[0], data)
                    continue
                log.info("Client closed the socket. Allocating its block...")
                open_sockets.remove(sock)
                if len(open_sockets) < config.getint("main", "blocks"):
                    res.alloc()


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARN)
    main()
