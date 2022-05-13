#!/bin/bash
docker run --name wiz --restart=always -it -d -v  /home/hik-vps/wizdata:/wiz/storage -v  /etc/localtime:/etc/localtime -p 3080:80 -p 9269:9269/udp -e SEARCH=true  wiznote/wizserver:latest
