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
from requests import get
import logging
import random
import threading
from urllib.parse import urlparse
import json
import pdb
from scraperpipeline.models import substacknewsletter, sitemap, newsletterPostUrls, newsletterscrapestatus, postsToIgnore 


def getAbout(url):
    # url = u + '/about/'
    # if u[-1] == '/':
    #     url = u + 'about'
    resp = get(url)

    soup = BeautifulSoup(resp.text,'html.parser')
    text = ''

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
    serializedData = json.dumps(myarray)
    #print (serializedData)

    data_file = open("/tmp/inputfile.json", 'w')
    data_file.write(serializedData)
    data_file.close()
    command = "cd && cd blogSearch && node addDocuments.js structuredResults /tmp/inputfile.json"
    res = os.system(command)


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
        sitemapObjs = sitemap.objects.all();
        #was it created just now? 
        for idx,sitemapObj in enumerate(sitemapObjs):
            if idx < 200:
                continue
            #Parse xml
            # get root element
            try:
                #print (sitemapObj.text)
                root = ET.fromstring(sitemapObj.text)
                urlSet = set()
                #pdb.set_trace()
                for url in root:
                    #pdb.set_trace()
                    for elem in url:
                       # pdb.set_trace()
                        if (elem.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
                            if ("/p/" in elem.text):
                                #Found a new post. Store it in an object
                                newsletterPostUrl = elem.text
                                if postsToIgnore.objects.filter(url=newsletterPostUrl).exists():
                                    #logger.info("newsletterPostUrl=" + newsletterPostUrl +" is in ignore list. Ignoring it!")
                                    logger.info("BlogPost Url:"+newsletterPostUrl+" ignoring it")
                                    continue
                                urlSet.add(newsletterPostUrl)
                            elif ("/about" in elem.text):
                                #pdb.set_trace()
                                print(elem.text)
                                getAbout(elem.text)


                #Urls already in db but text not retrieved.
                newsletterPostUrlsObjs = newsletterPostUrls.objects.all().filter(parentnewsletter = sitemapObj.parentnewsletter).filter(origtext=None)
                for newsletterPostUrlsObj in newsletterPostUrlsObjs:
                    newsletterPostUrl = newsletterPostUrlsObj.url
                    #newsletterPostUrlsObj = newsletterPostUrls.objects.create(url=newsletterPostUrl, parentnewsletter = sitemapObj.parentnewsletter)
                    if postsToIgnore.objects.filter(url=newsletterPostUrl).exists():
                        logger.info("newsletterPostUrl=" + newsletterPostUrl +" is in ignore list. Ignoring it!")
                        continue
                        pdb.set_trace()
                        logger.info("Trying to hit newsletterPostUrl = " + newsletterPostUrl)
                        resp = requests.get(newsletterPostUrl,headers=defaultheaders)
                        logger.info("Response code is " + str(resp.status_code))
                        if resp.status_code == 200:
                            originalText = resp.content
                            newsletterPostUrlsObj.origtext = originalText
                            newsletterPostUrlsObj.save()
                        else:
                            #pdb.set_trace()
                            logger.error("Could not download text for " + newsletterPostUrl + " Got code " + str(resp.status_code))
                            postsToIgnoreObj[0] = postsToIgnore.objects.get_or_create(url=newsletterPostUrl)
                            postsToIgnoreObj[0].url = newsletterPostUrl
                            postsToIgnoreObj[0].countOfTriesSoFar = postsToIgnoreObj[0].countOfTriesSoFar + 1
                            postsToIgnoreObj[0].errMsg = str(postsToIgnoreObj[0].errMsg) + " Could not download text. resp_code = "
                            + str(resp.status_code) + " resp=" + resp.content
                            postsToIgnoreObj[0].save()


                #Urls not yet in db.
                newsletterPostUrlsObjs = newsletterPostUrls.objects.all().filter(parentnewsletter = sitemapObj.parentnewsletter).exclude(origtext=None)
                for newsletterPostUrlsObj in newsletterPostUrlsObjs:
                    urlSet.remove(newsletterPostUrlsObj.url)

                #logger.info("urlset is")
                #logger.info(urlSet)

                for newsletterPostUrl in urlSet:
                    if postsToIgnore.objects.filter(url=newsletterPostUrl).exists():
                        logger.info("newsletterPostUrl=" + newsletterPostUrl +" is in ignore list. Ignoring it!")
                        continue
                    #pdb.set_trace()
                    logger.info("Trying to hit newsletterPostUrl = " + newsletterPostUrl)
                    resp = requests.get(newsletterPostUrl,headers=defaultheaders)
                    logger.info("Response code is " + str(resp.status_code))
                    if resp.status_code == 200:
                        newsletterPostUrlsObj = newsletterPostUrls.objects.create(url=newsletterPostUrl, parentnewsletter = sitemapObj.parentnewsletter)
                        originalText = resp.content
                        newsletterPostUrlsObj.origtext = originalText
                        newsletterPostUrlsObj.save()
                    else:
                        #pdb.set_trace()
                        logger.error("Could not download text for " + newsletterPostUrl + " Got code " + str(resp.status_code))
                        postsToIgnoreObj[0] = postsToIgnore.objects.get_or_create(url=newsletterPostUrl)
                        postsToIgnoreObj[0].url = newsletterPostUrl
                        postsToIgnoreObj[0].countOfTriesSoFar = postsToIgnoreObj[0].countOfTriesSoFar + 1
                        postsToIgnoreObj[0].errMsg = str(postsToIgnoreObj[0].errMsg) + " Could not download text. resp_code = "
                        + str(resp.status_code) + " resp=" + resp.content
                        postsToIgnoreObj[0].save()



                print ("===")
            except Exception as e:
                logger.info("encountered exception. idx= " + str(idx) +  " sitemap is " +str(sitemapObj))
                logger.info(e)
                #pdb.set_trace()
                try:
                    postsToIgnoreObj = postsToIgnore.objects.get_or_create(url=newsletterPostUrl)
                    postsToIgnoreObj[0].url = newsletterPostUrl
                    postsToIgnoreObj[0].countOfTriesSoFar = postsToIgnoreObj[0].countOfTriesSoFar + 1
                    postsToIgnoreObj[0].errMsg = str(postsToIgnoreObj[0].errMsg) + " Could not download text. exception=" + str(e)
                    postsToIgnoreObj[0].save()
                except NameError:
                    logger.info("Name error :(")
            if (idx % 10 == 9):
                logger.info("Finished " + str(idx) + " urls so far")
            if (idx >= 500):
                logger.info("Exiting because we reached max index. idx=" + str(idx))
                sys.exit(0)
            time.sleep(1)  
          


