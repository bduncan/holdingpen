#!/usr/bin/env python
# vim: fileencoding=utf-8:

import os
import socket
import ConfigParser
import errno
import select
from contextlib import closing


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
            self._blocks.append(mmap.mmap(-1, self._blocksize, 0x2000))
            self._blocks[-1].write(''.join([random.randint(0, 256)
                                            for x in range(self._blocksize)]))

    def free(self):
        if len(self._blocks) > 0:
            mmap.munmap(self._blocks[-1])
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
            os.unlink("tmp/%d" % (self._i))
            self._i -= 1

    def __len__(self):
        return len(os.listdir("tmp"))


def main():
    defaults = {"socket": "/var/run/holdingpen.socket",
                "blocksize": str(1024 * 1024),
                "blocks": "2"}
    config = ConfigParser.SafeConfigParser(defaults)
    config.read('/etc/holdingpen.conf')
    with closing(socket.socket(socket.AF_UNIX)) as listen_sock:
        # Unix sockets can't be reused. This seems to be how people handle it.
        os.unlink(config.get("main", "socket"))
        listen_sock.bind(config.get("main", "socket"))
        listen_sock.listen(5)
        res = FileStack(config.getint("main", "blocks"),
                        config.getint("main", "blocksize"))
        while True:
            # select without timeout
            r, w, x = select.select([listen_sock] + open_sockets, [], [])
            if listen_sock in r:
                open_sockets.append(listen_sock.accept())
                if len(res):
                    res.free()
                    log.info("Allocated a block to client on %r",
                        open_sockets[-1])
                else:
                    log.warn("Ran out of blocks to allocate to client on %r",
                        open_sockets[-1])
            else:
                err = r[0].recv(1)
                if err != -1:
                    log.warn("Client sent some data! Really just expected the"
                          + " socket to close...")
                    log.warn(str(err))
                    continue
                res.alloc()


if __name__ == '__main__':
    main()
