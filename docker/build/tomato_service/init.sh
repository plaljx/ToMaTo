#!/bin/bash

if ! [ -f /config/service.pem ]; then
  openssl req -new -x509 -days 1000 -nodes -out /config/service.pem -keyout /config/service.pem -subj /CN=`hostname`/ -batch
fi

if ! [ -f /config/ca.pem ]; then
  touch /config/ca.pem
fi

echo "$TIMEZONE" > /etc/timezone
cp "/usr/share/zoneinfo/$TIMEZONE" /etc/localtime