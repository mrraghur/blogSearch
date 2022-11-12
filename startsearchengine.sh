#!/usr/bin/bash                                                                                                    
  
set -x

source config.sh
#Script to start typsense server, read db.sqlite data and post documents to search engine.                         
#A different process will start the populate db.sqlite

#https://stackoverflow.com/questions/18622907/only-mkdir-if-it-does-not-exist
#Create directory if it does not exist
if [ ! -d $TYPESENSE_DATA_DIR ]; then
  mkdir $TYPESENSE_DATA_DIR
fi

#Start typesense server on port 8108 (which hopefully is not occupied)
nohup typesense-server --data-dir=$TYPESENSE_DATA_DIR --api-key=xyz --listen-port 8108 --enable-cors &

node createSchemaBlogs.js && node createSchemaStructuredResults.js


#Build frontend
#sudo rm -r dist # If dist/ is already present
#parcel build index.html
#sudo rm -rf /var/www/blogSearch/dist
#sudo mv -f dist/ /var/www/blogSearch/


#Post new data to the search engine index
source ${VENVPATH}/bin/activate
python3 manage.py postToTypeSense
