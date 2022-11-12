from __future__ import division
from django.core.management.base import BaseCommand, CommandError
from requests.exceptions import SSLError
from django.db import connection, transaction
from django.db import transaction
from django.db import connection
from django.db import reset_queries
import requests
import sys
import json
import pdb
import traceback
import time
import logging
import timeit
import re
import datetime
import atexit
import os
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import nltk, re, pprint

import logging
import random
import threading
from urllib.parse import urlparse
import json
from scraperpipeline.models import substacknewsletter, aboutme


##Go through all objects in aboutme table  and add them to typesense search engine.

logger = logging.getLogger('django')
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
#user_agent = {'User-agent': 'Mozilla/5.0'}
defaultheaders = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'    
}

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    maxNumLines = None
    args = None
    leftovers = None

    def add_arguments(self, parser):
        pass
        #parser.add_argument('jsonfilesfromalgolia', nargs='+', type=str, help='json files from algolia') 
        #parser.add_argument('--continueDownloading', action='store_true', help="Download MAX_NUM_ITEMS_TO_DOWNLOAD from where we left off last time")
        #parser.add_argument('--downloadArticlesFromNewsWebsites', action='store_true', help=" download content of links posted to HN")
        #parser.add_argument('--runUnitTests', action='store_true', help="Run  unit tests through database and find who are founders of what company")


        self.args, self.leftovers = parser.parse_known_args()


    def handle(self, *args, **options):
        idx = 0
        #pdb.set_trace()

        totalNumPosts = aboutme.objects.all().count()
        logger.info("Will be ingesting a total of " + str(totalNumPosts))
        batchSize = 100
        
        for idx in range(0,totalNumPosts,batchSize):
            start = idx
            end = idx+batchSize
            #if idx == 13000:
            #    end = 13890
            # pdb.set_trace()
            aboutmeObjs = aboutme.objects.all()[start:end]

            for aboutmeObj in aboutmeObjs:
                print(idx)
                #collect individual object from database instead of all.
                idx = idx+1
                #if (idx < 13890):
                #    continue
                url = aboutmeObj.url
                text = aboutmeObj.text

                mydict = {
                       "text":text,
                       "url":url
                       }




                myarray = []
                myarray.append(mydict)
                serializedData = json.dumps(myarray)
                #print (serializedData)

                data_file = open("/tmp/inputfile.json", 'w')
                data_file.write(serializedData)
                data_file.close()
                #Run from the same directory as code
                #TODO: Add a config for code directory, etc
                command = "node addDocuments.js structuredResults /tmp/inputfile.json"
                res = os.system(command)

            #if (idx >= 2):
            #    sys.exit(10)
            if (idx % 10 == 0):
                print ("Finished " + str(idx) + "-------------");
            #except Exception as e:
            #    logger.info("encountered exception. idx= " + str(idx) +  " sitemap is " +str(sitemapObj))            #    logger.info(e)

            #    #pdb.set_trace()
            #if (idx % 10 == 9):
            #    logger.info("Finished " + str(idx) + " urls so far")
            if (idx >= 5):
                logger.info("Exiting because we reached max index. idx=" + str(idx))
                sys.exit(0)
            time.sleep(0.1)
