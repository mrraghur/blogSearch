#!/usr/bin/bash

set -x

source config.sh

#Script to do one line install of typesense search engine and create appropriate tables
#To be run from inside the github repo

#TODO: Someday, we will need t upgrade the server version.
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
     ls typesense-server || wget https://dl.typesense.org/releases/0.21.0/typesense-server-0.21.0-linux-amd64.tar.gz
     ls typesense-server-0.21.0-linux-amd64.tar.gz && tar -xvzf typesense-server-0.21.0-linux-amd64.tar.gz
elif [[ "$OSTYPE" == "darwin"* ]]; then
        # Mac OSX
        ls typesense-server || wget https://dl.typesense.org/releases/0.21.0/typesense-server-0.21.0-darwin-amd64.tar.gz
        ls typesense-server-0.21.0-darwin-amd64.tar.gz && tar -xvzf typesense-server-0.21.0-darwin-amd64.tar.gz
elif [[ "$OSTYPE" == "cygwin" ]]; then
        # POSIX compatibility layer and Linux environment emulation for Windows
        echo "Unsupported OS. $OSTYPE"
elif [[ "$OSTYPE" == "msys" ]]; then
        # Lightweight shell and GNU utilities compiled for Windows (part of MinGW)
        echo "Unsupported OS. $OSTYPE"
elif [[ "$OSTYPE" == "win32" ]]; then
        # I'm not sure this can happen.
        echo "Unsupported OS. $OSTYPE"
elif [[ "$OSTYPE" == "freebsd"* ]]; then
        echo "Unsupported OS. $OSTYPE"
else
        # Unknown.
        echo "Unsupported OS. $OSTYPE"
fi


#https://stackoverflow.com/questions/18622907/only-mkdir-if-it-does-not-exist
#Create directory if it does not exist
if [ ! -d $TYPESENSE_DATA_DIR ]; then
  mkdir $TYPESENSE_DATA_DIR
fi

#Install npm related packages for instant search and UI
if [ ! -d $VENVPATH ]; then
    python3 -m venv $VENVPATH
fi
source $VENVPATH/bin/activate

#install nopm dependencies.
npm i 

#install python requirements for the scraper, one package at a time so that unexpected errors wont stop the whole process
#TODO: Normally, we want atomic operations, but that takes time and effort.
cat requirements.txt | while read LINE; do
    pip install $LINE
    done
