#!/bin/bash

cd "${0%/*}"

echo "---"
echo "deploying to https://julianstahnke.com/html/scrapper-static"
echo "---"

rsync -r -v --checksum --delete --human-readable --progress scraps.db "jujulian@julianstahnke.com:/home/jujulian/scrapper/scraps.db"

# copy all files
# compare checksums so only files with changed content are copied
# to prevent uncaching them
rsync --rsync-path="mkdir -p /home/jujulian/html/static-scrapper/ && rsync" -r -v --checksum --delete --perms --chmod=Du=rwx,Dgo=rx,Fu=rw,Fgo=r --human-readable --progress static/ "jujulian@julianstahnke.com:/home/jujulian/html/static-scrapper/"
