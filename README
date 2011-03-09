Holding Pen
===========

This is a program which reserves some resource for later use. For example, it
pre-allocates memory such that another program can use it later when the
machine is more heavily loaded. It can do the same thing with disk space.

The daemon works by listening on a unix domain socket (by default at
/var/run/holdingpen.socket), optionally with given permissions. When a
connection is made to this socket, one of a pool of previously allocated
resources is freed. Then, hopefully, the application will be able to take
ownership of this resource. Once the socket is closed, the daemon attempts to
reallocate the resource so that it may be used by the next client.

There is a wrapper script which makes a connection to the daemon and execs the
given program. The program should inherit the open socket to the daemon and,
when it exits, the socket will automatically be closed, instructing the daemon
to assume ownership of the resource again.

Our use case
------------

We have a pool of workstations to be used for teaching classes. The pool is
specified so that remote users may get an NX remote login session on one of the
machines to do research. This research can occasionally be very resource
intensive and even if each user is working within their means, there may be
multiple remote users on one machine. We plan to use Holding Pen to allow
console users to always have memory available to run MATLAB, regardless of what
else the machine is doing. We plan to give ownership of the socket to the
console user through gdm.

TODO
----

The daemon needs an init script.
Some documentation about how to actually use it! Dependent on the previous step.
Unix sockets allow file descriptors to be passed between processes. This could
    remove the race condition between the daemon freeing the resource and the
    application requesting it.
Packaging as deb (or rpm).

Copyright, Author, License
--------------------------

This software was written by Bruce Duncan at the University of Edinburgh in
2011 in the course of employment.

Copyright (C) 2011 Bruce Duncan, University of Edinburgh

This program is licensed under the GNU General Public License version 3. The
license is in the file COPYING.
