#!/usr/bin/bash
  
set -x

#Script to start typsense server, read db.sqlite data and post documents to search engine.
#A different process will start the populate db.sqlite

#https://stackoverflow.com/questions/18622907/only-mkdir-if-it-does-not-exist
#Create directory if it does not exist
TYPESENSE_DATA_DIR="/tmp/typesense-data3"
if [ ! -d $TYPESENSE_DATA_DIR ]; then
  mkdir $TYPESENSE_DATA_DIR
fi

#Start typesense server on port 8108 (which hopefully is not occupied)
nohup typesense-server --data-dir=/tmp/typesense-data --api-key=xyz --listen-port 8108 --enable-cors &

node createSchemaBlogs.js && node createSchemaStructuredResults.js

cd substacksearchengine

#Build frontend
rm -r dist # If dist/ is already present
parcel build index.html
rm -rf /var/www/blogSearch
mv dist/ /var/www/blogSearch/


#Post new data to the search engine index
source $VENVPATH/bin/activate
python manage.py postToTypeSense
