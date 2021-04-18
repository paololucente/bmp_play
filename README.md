# bmp_play
A small utility, written in Python, to record and replay BMP packets
very useful for devloping around the protocol.

Originally part of OpenBMP dev tools, it eventually disappeared from
the known cyber space. The idea is to make this tool public again for
the community to enjoy and improve. 

To record: bmp_play.py -m record -p 1790 -f bmp.dump

To replay: bmp_play.py -m play -p 1790 -f bmp.dump -d 127.0.0.1

More Examples:
replay 3 times the dump with 60sec delay between the dumps and terminate automaticly after finishing by using python3.7 
python3.7 /opt/daisy/bin/bmp_play/bmp_play.py -m play -p 1791 -f /opt/daisy/bin/bmp_play/bmp.dump -d 10.0.10.11 -l 3 -i 60 -e

replay for ever the dump with 120sec delay between the dumps by using python2.7 
python2 /opt/daisy/bin/bmp_play/bmp_play.py -m play -p 1791 -f /opt/daisy/bin/bmp_play/bmp.dump -d 10.0.10.11 -l 0 -i 120
