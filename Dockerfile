# This is the Dockerfile that will create the image for PyCloud
FROM python:3.6

WORKDIR /tmp

ADD . .

RUN pip3 install . && rm -Rf /tmp

CMD ['python3', '-m', 'pycloud.app']
