#!/usr/bin/bash

set -x

#Script to start typsense server, read db.sqlite data and post documents to search engine.
#A different process will start the populate db.sqlite

#Start typesense server on port 8108 (which hopefully is not occupied)
nohup typesense-server --data-dir=/tmp/typesense-data --api-key=xyz --listen-port 8108 --enable-cors &

node createSchemaBlogs.js && node createSchemaStructuredResults.js

cd substacksearchengine



