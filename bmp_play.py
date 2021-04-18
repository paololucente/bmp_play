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

            print("Connected: ", addr)

            if (cfg['router'] and not addr[0] == cfg['router']):
                print(" ... router does not equal %s, skipping", addr[0])
                conn.close()
                continue

            with open(cfg['file'], "wb") as f:
                while True:
                    data = conn.recv(1024)
                    if (not data):
                        break

                    f.write(data)

            print(" ...Done")

            run = False


    except socket.error as msg:
        print("ERROR: failed to record: %r", msg)

def play(cfg):
    """ Play BMP messages by sending recorded BMP stream from file to destip/port """
    try:
	# Some config validations first
        if cfg['loop'] == None:
            loopval = 1
        elif cfg['loop']:
            loopval = int(cfg['loop'])

	    if (loopval < 0):
                print("ERROR: Invalid 'loop' value")
                sys.exit(3)

	    if (loopval == 0 and cfg['keep_open']):
                print("ERROR: 'keep_open' does not apply to infinite 'loop' value")
                sys.exit(3)
        else:
            loopval = 1

        if cfg['interval'] == None:
            interval = 0
        elif cfg['interval']:
            interval = int(cfg['interval'])

	    if (interval < 0):
                print("ERROR: Invalid 'interval' value")
                sys.exit(3)
        else:
            interval = 0

        sock =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # spoof a router addr if requested, use "net.ipv4.ip_nonlocal_bind=1" as needed 
        if (cfg['router']):
            sock.bind((cfg['router'], 0))

        sock.connect((cfg['dest_addr'], cfg['port']))
        print("Connected, sending data...")

        if int(cfg['loop']) != 0:
            print("Looping %s times over input file" % int(cfg['loop']))
            for val in range(0, int(cfg['loop'])):
                sys.stdout.write('.')
                sys.stdout.flush()
                with open(cfg['file'], "rb") as f:
                    while True:
                        data = f.read(1024)
        
                        if (not data):
                            break;
        
                        data = sock.sendall(data)
                sleep(interval)

        else:
            print("Looping forever until Ctrl-C")
            while True:
                sys.stdout.write('.')
                sys.stdout.flush()
                with open(cfg['file'], "rb") as f:
                    while True:
                        data = f.read(1024)
        
                        if (not data):
                            break;
        
                        data = sock.sendall(data)
                sleep(interval)
                    
        if cfg['keep_open'] == None:
            print("\n...Done   Closing connection.")
        else:
            print("\n...Done   Press Ctrl-C to close connection.")
            while True:
                sleep(1)

    except socket.error as msg:
        print("ERROR: failed to play: %r", msg)
            

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
                    loop:       <loop number of interations>
                    interval:   <delay between the loop iterations>
                    keep_open:  <don't close the TCP session after play>
                }
    """
    REQUIRED_ARGS = 3
    found_req_args = 0
    cmd_args = { 'mode': None,
                 'port': None,
                 'filename': None,
                 'dest_addr': None,
                 'router': None,
                 'loop': None,
                 'interval': None,
                 'keep_open': None }

    if (len(argv) < 3):
        print("ERROR: Missing required args")
        usage(argv[0])
        sys.exit(1)

    try:
        (opts, args) = getopt.getopt(argv[1:], "hkm:p:f:r:d:l:i:",
                                       ["help", "mode=", "port=", "file=", "router=", "destip=", "loop=", "interval=", "keep_open"])

        for o, a in opts:
            if o in ("-h", "--help"):
                usage(argv[0])
                sys.exit(0)

            elif o in ("-m", "--mode"):
                found_req_args += 1
                if (a in ['record', 'play']):
                    cmd_args['mode'] = a
                else:
                    print("ERROR: Invalid mode of '%s", a)
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

            elif o in ("-l", "--loop"):
                cmd_args['loop'] = a

            elif o in ("-i", "--interval"):
                cmd_args['interval'] = a

            elif o in ("-k", "--keep-open"):
                cmd_args['keep_open'] = True

            else:
                usage(argv[0])
                sys.exit(1)

        if (found_req_args < REQUIRED_ARGS):
            print("ERROR: Missing required args, found %d required %d", found_req_args, REQUIRED_ARGS)
            usage(argv[0])
            sys.exit(1)

        elif (cmd_args['mode'] == 'play'): 
            if (cmd_args['dest_addr'] == None):
                print("ERROR: play mode requires destination IP arg")
                usage(argv[0])
                sys.exit(1)

        return cmd_args

    except (getopt.GetoptError, TypeError) as err:
        print("%s", str(err)) # will print something like "option -a not recognized"
        usage(argv[0])
        sys.exit(2)


def usage(prog):
    """ Usage - Prints the usage for this program.

        :param prog:  Program name
    """
    print("")
    print("Usage: %s [OPTIONS]", prog)
    print("")

    print("REQUIRED OPTIONS:")
    print("  -m, --mode".ljust(30) + "Either 'record' or 'play'")
    print("  -p, --port".ljust(30) + "TCP Port to listen on or to send to")
    print("  -f, --file".ljust(30) + "Filename to write to or read from")
    print("  -d, --destip".ljust(30) + "For play mode; Destination IP address of collector")
    print("")

    print("OPTIONAL OPTIONS:")
    print("  -h, --help".ljust(30) + "Print this help menu")
    print("  -r, --router".ljust(30) + "Router IP address to accept (record) or spoof (play)")
    print("  -l, --loop".ljust(30) + "How many times to process the dump file (play) [default: 1]")
    print("  -i, --interval".ljust(30) + "Interval between dump file plays (play)")
    print("  -k, --keep-open".ljust(30) + "Once finished playing, keep the TCP session up (play)")


def main():
    """
        Start of program from shell
    """
    cfg = parseCmdArgs(sys.argv)

    if (cfg['mode'] == 'record'):
        print("Listening for connection...")
        record(cfg)

    elif (cfg['mode'] == 'play'):
        print("Sending contents of '%s' to connection to %s", cfg['file'], cfg['dest_addr'])
        play(cfg)


if __name__ == '__main__':
    main()
