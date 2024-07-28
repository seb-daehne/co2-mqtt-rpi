FROM  arm32v6/alpine:3.20
#FROM  alpine:3.9
ADD qemu-arm-static /usr/bin

# update and add dependencies
RUN apk update && apk upgrade && \
    apk add tzdata curl wget bash python py-paho-mqtt && \
    rm -rf /var/cache/apk/*

ADD read_co2.py /
CMD [ "python" , "/read_co2.py"]
