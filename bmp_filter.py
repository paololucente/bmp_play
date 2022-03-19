#!/usr/bin/env python
"""
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

import argparse
import mmap

message_type_map = {
    0: "Route Monitoring",
    1: "Statistics Report",
    2: "Peer Down Notification",
    3: "Peer Up Notification",
    4: "Initiation Message",
    5: "Termination Message",
    6: "Route Mirroring Message",
}


class Statistics:
    def __init__(self):
        self.kept = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
        }

        self.discarded = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
        }

    def print(self):
        print(f'### PACKETS KEPT ###')
        print(f'Route Monitoring:\t\t{self.kept[0]}')
        print(f'Statistics Report:\t\t{self.kept[1]}')
        print(f'Peer Down Notification:\t\t{self.kept[2]}')
        print(f'Peer Up Notification:\t\t{self.kept[3]}')
        print(f'Initiation Message:\t\t{self.kept[4]}')
        print(f'Termination Message:\t\t{self.kept[5]}')
        print(f'Route Mirroring Message:\t{self.kept[6]}')

        print(f'### PACKETS DISCARDED ###')
        print(f'Route Monitoring:\t\t{self.discarded[0]}')
        print(f'Statistics Report:\t\t{self.discarded[1]}')
        print(f'Peer Down Notification:\t\t{self.discarded[2]}')
        print(f'Peer Up Notification:\t\t{self.discarded[3]}')
        print(f'Initiation Message:\t\t{self.discarded[4]}')
        print(f'Termination Message:\t\t{self.discarded[5]}')
        print(f'Route Mirroring Message:\t{self.discarded[6]}')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Filter BMP message from record')
    parser.add_argument(
        '-i',
        '--input',
        dest="input",
        type=str,
        required=True,
        help="Input file",
    )

    parser.add_argument(
        '-o',
        '--output',
        dest="output",
        type=str,
        required=True,
        help="Output file",
    )

    parser.add_argument(
        '--route-monitoring',
        dest="rm",
        action='store_true',
        help="Include router monitoring messages",
    )

    parser.add_argument(
        '--statistics-report',
        dest="stats",
        action='store_true',
        help="Include Statistics Report messages",
    )

    parser.add_argument(
        '--peer-down',
        dest="pd",
        action='store_true',
        help="Include Peer Down Notification messages",
    )

    parser.add_argument(
        '--peer-up',
        dest="pu",
        action='store_true',
        help="Include Peer Up Notification messages",
    )

    parser.add_argument(
        '--initiation',
        dest="init",
        action='store_true',
        help="Include Initiation Message messages",
    )

    parser.add_argument(
        '--termination',
        dest="term",
        action='store_true',
        help="Include Termination Message messages",
    )

    parser.add_argument(
        '-m',
        '--route-mirroring',
        dest="rmirror",
        action='store_true',
        help="Include Route Mirroring messages",
    )

    args = parser.parse_args()
    return args


def args_to_filter_map(args):
    return {
        0: not args.rm,
        1: not args.stats,
        2: not args.pd,
        3: not args.pu,
        4: not args.init,
        5: not args.term,
        6: not args.rmirror,
    }


def decode_common_header(header):
    version = int(header[0])
    msg_length = int.from_bytes(header[1:5], byteorder='big', signed=False)
    msg_type = header[5]
    return version, msg_length, msg_type


def main():
    args = parse_args()
    filter_map = args_to_filter_map(args)
    statistics = Statistics()

    with open(args.input, 'rb') as inp:
        with mmap.mmap(inp.fileno(), 0, access=mmap.ACCESS_READ) as inp_map:
            with open(args.output, 'wb') as out:
                head = 0
                while head < len(inp_map):
                    version, msg_length, msg_type = decode_common_header(
                        inp_map[head:head+6])
                    if not filter_map[msg_type]:
                        statistics.kept[msg_type] += 1
                        out.write(inp_map[head:head+msg_length])
                    else:
                        statistics.discarded[msg_type] += 1

                    head += msg_length
    statistics.print()


if __name__ == '__main__':
    main()
