#!/usr/bin/env python
"""
  Copyright (c) 2015 Cisco Systems, Inc. and others.  All rights reserved.

  This program and the accompanying materials are made available under the
  terms of the Eclipse Public License v1.0 which accompanies this distribution,
  and is available at http://www.eclipse.org/legal/epl-v10.html

  .. moduleauthor:: Tim Evens <tievens@cisco.com>
"""
import sys
import getopt
import socket
from time import sleep


def record(cfg):
    """ Record BMP messages by listening on port and writing to file

        :param cfg:     Config dictionary
    """

    try:
        sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', cfg['port']))
        sock.listen(1)

        run = True
        while (run):
            (conn, addr) = sock.accept()

            print "Connected: ",addr

            if (cfg['router'] and not addr[0] == cfg['router']):
                print " ... router does not equal %s, skipping" % addr[0]
                conn.close()
                continue

            with open(cfg['file'], "wb") as f:
                while True:
                    data = conn.recv(1024)
                    if (not data):
                        break

                    f.write(data)

            print " ...Done"

            run = False


    except socket.error as msg:
        print "ERROR: failed to record: %r" % msg

def play(cfg):
    """ Play BMP messages by sending recorded BMP stream from file to destip/port """
    try:
        sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # spoof a router addr if requested, use "net.ipv4.ip_nonlocal_bind=1" as needed 
        if (cfg['router']):
            sock.bind((cfg['router'], 0))

        sock.connect((cfg['dest_addr'], cfg['port']))
        print "Connected, sending data..."

        with open(cfg['file'], "rb") as f:
            while True:
                data = f.read(1024)

                if (not data):
                    break;

                data = sock.sendall(data)
                
        print " ...Done   press Ctrl-C to close connection"
 
        while True:
           sleep(1)

    except socket.error as msg:
        print "ERROR: failed to play: %r" % msg
            

def parseCmdArgs(argv):
    """ Parse commandline arguments

        Usage is printed and program is terminated if there is an error.

        :param argv:   ARGV as provided by sys.argv.  Arg 0 is the program name

        :returns:  dictionary defined as::
                {
                    mode:       <mode as either 'play' or 'record'>,
                    port:       <int port number>,
                    file:       <filename to write to or read from>,
                    dest_addr:  <Destination address for play mode>,
                    router:     <router IP address to accept or spoof>
                }
    """
    REQUIRED_ARGS = 3
    found_req_args = 0
    cmd_args = { 'mode': None,
                 'port': None,
                 'filename': None,
                 'dest_addr': None,
                 'router': None }

    if (len(argv) < 3):
        print "ERROR: Missing required args"
        usage(argv[0])
        sys.exit(1)

    try:
        (opts, args) = getopt.getopt(argv[1:], "hm:p:f:r:d:",
                                       ["help", "mode=", "port=", "file=", "router=", "destip="])

        for o, a in opts:
            if o in ("-h", "--help"):
                usage(argv[0])
                sys.exit(0)

            elif o in ("-m", "--mode"):
                found_req_args += 1
                if (a in ['record', 'play']):
                    cmd_args['mode'] = a
                else:
                    print "ERROR: Invalid mode of '%s" % a
                    usage(argv[0])
                    sys.exit(1)

            elif o in ("-p", "--port"):
                found_req_args += 1
                cmd_args['port'] = int(a)

            elif o in ("-f", "--file"):
                found_req_args += 1
                cmd_args['file'] = a

            elif o in ("-r", "--router"):
                cmd_args['router'] = a

            elif o in ("-d", "--destip"):
                cmd_args['dest_addr'] = a

            else:
                usage(argv[0])
                sys.exit(1)

        if (found_req_args < REQUIRED_ARGS):
            print "ERROR: Missing required args, found %d required %d" % (found_req_args, REQUIRED_ARGS)
            usage(argv[0])
            sys.exit(1)

        elif (cmd_args['mode'] == 'play'): 
            if (cmd_args['dest_addr'] == None):
                print "ERROR: play mode requires destination IP arg"
                usage(argv[0])
                sys.exit(1)

        return cmd_args

    except (getopt.GetoptError, TypeError), err:
        print str(err)  # will print something like "option -a not recognized"
        usage(argv[0])
        sys.exit(2)


def usage(prog):
    """ Usage - Prints the usage for this program.

        :param prog:  Program name
    """
    print ""
    print "Usage: %s [OPTIONS]" % prog
    print ""

    print "REQUIRED OPTIONS:"
    print "  -m, --mode".ljust(30) + "Either 'record' or 'play'"
    print "  -p, --port".ljust(30) + "TCP Port to listen on or to send to"
    print "  -f, --file".ljust(30) + "Filename to write to or read from"
    print "  -d, --destip".ljust(30) + "For play mode; Destination IP address of collector"
    print ""

    print "OPTIONAL OPTIONS:"
    print "  -h, --help".ljust(30) + "Print this help menu"
    print "  -r, --router".ljust(30) + "Router IP address to accept (record) or spoof (play)"


def main():
    """
        Start of program from shell
    """
    cfg = parseCmdArgs(sys.argv)

    if (cfg['mode'] == 'record'):
        print "Listening for connection..."
        record(cfg)

    elif (cfg['mode'] == 'play'):
        print "Sending contents of '%s' to connection to %s" % (cfg['file'], cfg['dest_addr'])
        play(cfg)


if __name__ == '__main__':
    main()
