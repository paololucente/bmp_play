# bmp_play
A small utility, written in Python, to record and replay BMP packets
very useful for devloping around the protocol.

Originally part of OpenBMP dev tools, it eventually disappeared from
the known cyber space. The idea is to make this tool public again for
the community to enjoy and improve. 

To record: `bmp_play.py -m record -p 1790 -f bmp.dump`

To replay: `bmp_play.py -m play -p 1790 -f bmp.dump -d 127.0.0.1`

### More Examples:
- Replay a dump 3 times with 60 secs delay between the plays. Once finished, keep the TCP connection up:
  * `bmp_play.py -m play -p 1790 -f bmp.dump -d 127.0.0.1 -l 3 -i 60 -k`

- Replay a dump forever with 120 secs delay between the plays:
  * `bmp_play.py -m play -p 1790 -f bmp.dump -d 127.0.0.1 -l 0 -i 120`
