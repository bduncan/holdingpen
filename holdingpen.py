#!/usr/bin/env python
# vim: fileencoding=utf-8:

import os
import socket
import ConfigParser

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
    def alloc(self):
        self._blocks.append(mmap.mmap(-1, self._blocksize, 0x2000)) # MAP_LOCKED
        self._blocks[-1].write(''.join([random.randint(0, 256) for x in range(self._blocksize)]))

    def free(self):
        mmap.munmap(self._blocks[-1])
        del self._blocks[-1]

    def __len__(self):
        return len(self._blocks)


def main():
    defaults = {"socket": "/var/run/holdingpen.socket",
                "blocksize": 1024*1024,
                "blocks": 2}
    config = ConfigParser.SafeConfigParser(defaults)
    config.read('/etc/holdingpen.conf')
    listen_sock = socket.socket(socket.AF_UNIX, config.get("main", "socket"))
    blocks = []
    for i in range(config.getint("main", "blocks")):
        alloc(blocks, config.getint("main", "blocksize"))
    open_sockets = []
    while True:
        r,w,x = select.select([listen_sock] + open_sockets, [], []) # no timeout
        if listen_sock in r:
            open_sockets.append(listen_sock.accept())
            if blocks:
                log.info("Allocated a block to client on %r", open_sockets[-1])
            else:
                log.warn("Ran out of blocks to allocate to client on %r", open_sockets[-1])
        else:
            err = r[0].recv(1)
            if err != -1:
                log.warn("Client sent some data! Really just expected the socket to close...")
                log.warn(str(err))
                continue
            if len(blocks) < config.getint("main", "blocks"):
                alloc(blocks, config.getint("main", "blocksize"))

if __name__ == '__main__':
    main()
