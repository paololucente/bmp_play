# bmp_play
A small utility, written in Python, to record and replay BMP packets
very useful for devloping around the protocol.

Originally part of OpenBMP dev tools, it eventually disappeared from
the known cyber space. The idea is to make this tool public again for
the community to enjoy and improve. 

To record: bmp_play.py -m record -p 1790 -f bmp.dump

To replay: bmp_play.py -m play -p 1790 -f bmp.dump -d 127.0.0.1
