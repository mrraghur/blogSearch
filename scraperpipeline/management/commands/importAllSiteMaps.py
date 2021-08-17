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
from requests import get
import pandas as pd
from bs4 import BeautifulSoup

import logging
import random
import threading
from urllib.parse import urlparse
import json
import pdb
from scraperpipeline.models import substacknewsletter, sitemap, newsletterPostUrls, newsletterscrapestatus


logger = logging.getLogger('django')
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


def getAbout(u):
    #pdb.set_trace()
    url = u + '/about/'
    if u[-1] == '/':
        url = u + 'about'
    resp = get(url)

    soup = BeautifulSoup(resp.text,'html.parser')
    text = ''
    print(url)
    dd = soup.find(class_='content-about')
    if dd != None:
        for d in dd:
            text = text + d.get_text() + ' '
    else:
        dd = soup.find_all('p')
        if dd != None:
            for d in dd:
                text = text + d.text + ' '

    mydict = {
        "text":text,
        "url":url
        }
    myarray = []
    myarray.append(mydict)
    #pdb.set_trace()
    serializedData = json.dumps(myarray)
    #print (serializedData)

    data_file = open("/tmp/inputfile.json", 'w')
    data_file.write(serializedData)
    data_file.close()
    #Run from the same directory where code is present.
    #TODO: Make it a little more configurable.
    command = "node addDocuments.js structuredResults /tmp/inputfile.json"
    res = os.system(command)    


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    maxNumLines = None
    args = None
    leftovers = None

    def add_arguments(self, parser):
        parser.add_argument('-jsonfilesfromalgolia', nargs='+', type=str, help='json files from algolia')
        #parser.add_argument('--continueDownloading', action='store_true', help="Download MAX_NUM_ITEMS_TO_DOWNLOAD from where we left off last time")
        #parser.add_argument('--downloadArticlesFromNewsWebsites', action='store_true', help=" download content of links posted to HN")
        #parser.add_argument('--runUnitTests', action='store_true', help="Run  unit tests through database and find who are founders of what company")


        self.args, self.leftovers = parser.parse_known_args()


    def handle(self, *args, **options):
        jsonfilesfromalgolia = options['jsonfilesfromalgolia']
        for jsonfilefromalgolia in jsonfilesfromalgolia:
            logger.info ("file is " + jsonfilefromalgolia)
            fp = open(jsonfilefromalgolia,)
            data = json.load(fp)
            hits= data["hits"]
            for hit in hits:
                substackurl = hit["url"]
                if substackurl is None or not "substack.com" in substackurl or "cdn.substack.com" in substackurl:
                    continue
                substackurlParseResult = urlparse(substackurl)
                print(substackurl)
                getAbout(substackurl)
                newsletterUrl = '{uri.scheme}://{uri.netloc}/'.format(uri=substackurlParseResult)
                sitemapUrlRaw = newsletterUrl+"/sitemap.xml"
                sitemapUrlParseResult = urlparse(sitemapUrlRaw)
                substacknewsletterObj = substacknewsletter.objects.get_or_create(url=newsletterUrl) 
                if not substacknewsletterObj:
                    logger.error("object did not get created. ")
                    pdb.set_trace()
                sitemapObj = sitemap.objects.all().filter(parentnewsletter__url=newsletterUrl)


                        #, parentType="newsletter")
                if sitemapObj: #if it already exists, don't do anything more.
                    continue
                #sitemapObj = sitemap.ojbects.get_or_create(parentnewsletter=substacknewsletterObj, parentType="newsletter")

                logger.info ("hitting sitemap url is " + sitemapUrlParseResult.geturl())
                #Download the sitemap file
                resp = requests.get(sitemapUrlParseResult.geturl())
                if (resp.status_code != 200):
                    logger.error("Response not 200. Something wrong. Dropping to pdb. Code is")
                    logger.error (resp)
                    logger.error (str(resp.content))
                    #pdb.set_trace();
                else:
                    #Write to sitemap object in db.
                    sitemapObj = sitemap.objects.create(parentType="newsletter")
                    sitemapObj.parentnewsletter=substacknewsletterObj[0]
                    sitemapXml = resp.text;
                    sitemapObj.text = sitemapXml;
                    sitemapObj.save();
                time.sleep(0.5)  

            

