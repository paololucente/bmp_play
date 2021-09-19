FROM python:3
COPY bmp_play.py /usr/bin
ENTRYPOINT [ "/usr/bin/bmp_play.py" ]