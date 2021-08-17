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
from scraperpipeline.models import substacknewsletter, sitemap, newsletterPostUrls, newsletterscrapestatus, postsToIgnore

import textstat
from textstat import flesch_reading_ease, dale_chall_readability_score_v2,gunning_fog,smog_index,automated_readability_index


##Go threw all objects in newsletterPostUrlsObjs and add them to typesense search engine.

logger = logging.getLogger('django')
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
#user_agent = {'User-agent': 'Mozilla/5.0'}
defaultheaders = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'    
}

#Higher the score, the more they have to learn.
# lfre of -80 is 5th grade but lfre of -10 is professional.
#ldcr of 6 is beginner, above 9 is professional etc
lfre,ldcr,lgfog,lsmog,lari = [-75,-50],[7,9],[9,12],[9,12],[9,12]


#https://stackoverflow.com/questions/26002076/python-nltk-clean-html-not-implemented
def clean_html(html):
    """
    Copied from NLTK package.
    Remove HTML markup from the given string.

    :param html: the HTML string to be cleaned
    :type html: str
    :rtype: str
    """

    # First we remove inline JavaScript/CSS:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    return cleaned.strip()

#Get class of the audience.
#cval of 0 is beginner, 1 is intermediate, 2 is expert.
def cc(val, lval):
    if val < lval[0]:
        cval = 0
    elif lval[0] <= val <= lval[1]:
        cval =  1
    elif lval[1] < val:
        cval =  2

    return cval


#Classifiy a given piece of text as beginner, intermediate or expert.
def getAudienceScore(text):
    #either link or text can be passed
    # resp = get(link)
    # soup = BeautifulSoup(resp.text,'html.parser')
    # text = ''
    # for d in soup.find_all('p',text=True):
    #     text = text + d.get_text() + ' '

    #Calculate readability index based on different models.
    fre = flesch_reading_ease(text)*-1
    dcr = dale_chall_readability_score_v2(text)
    gfog = gunning_fog(text)
    smog = smog_index(text)
    ari = automated_readability_index(text)

    #Take a vote between the five scores. Which ever category occurs most number of times wins.
    class_aud_list = [cc(fre,lfre),cc(dcr,ldcr),cc(gfog,lgfog),cc(smog,lsmog),cc(ari,lari)]

    #Calculate the value which occurs most often.
    class_aud = max(class_aud_list,key=class_aud_list.count)
    return text,class_aud

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
        #newsletterPostUrlsObjs = newsletterPostUrls.objects.all()#.filter(origtext==None)
        for i in range(0,1300,102):
            start = i
            end = i+10
            if i == 13000:
                end = 13890
            # pdb.set_trace()
            newsletterPostUrlsObjs = newsletterPostUrls.objects.all()[start:end]

            for newsletterPostUrlsObj in newsletterPostUrlsObjs:
                print(idx)
                #collect individual object from database instead of all.
                idx = idx+1
                #if (idx < 13890):
                #    continue
                newsletterPostUrl = newsletterPostUrlsObj.url
                text = newsletterPostUrlsObj.origtext
                parentnewsletter = newsletterPostUrlsObj.parentnewsletter
                title = parentnewsletter.url #slightly misleading but works for noe
                #pdb.set_trace()
                #Convert to json string
                if (newsletterPostUrlsObj.origtext == None):
                    continue
                soup = BeautifulSoup(newsletterPostUrlsObj.origtext, 'html.parser')
                #Get all images

                allimgs = set()
                #Save one randomly from the set
                for item in soup.find_all('img'):
                    imgsrc = item['src']
                    if (not "anonymous-head" in imgsrc) and (not imgsrc in allimgs):
                        #print(imgsrc)
                        allimgs.add(imgsrc)

                allimgsStr = ""
                if (len(allimgs) > 0):
                    allimgsStr = random.sample(allimgs, 1)
                    allimgsStr = allimgsStr[0]
                #pdb.set_trace()
                #pdb.set_trace()
                #soup = BeautifulSoup(html, 'html.parser')
                title = soup.find('title')
                #text = soup.get_text()
                texts = ''
                for text in soup.find_all('p'):
                    if text != None:
                        texts = texts + text.get_text()

                cleaned_text = clean_html(texts)#(.decode('UTF-8'))
                cleaned_text, audienceClass = getAudienceScore(cleaned_text)
                
                audienceClassStr = "beginner"
                if (audienceClass == 1):
                    audienceClassStr = "intermediate"
                elif (audienceClass == 2):
                    audienceClassStr = "expert"
                #pdb.set_trace()
                title = bytes(title.get_text(),'utf-8').decode("unicode_escape")
                mydict = {
                        'title':title,
                        "description":newsletterPostUrlsObj.url,
                        'category':"substack",
                        'url': newsletterPostUrlsObj.url,
                        'aud' : audienceClassStr,
                        'readingtime': random.randrange(0, 100),
                        'imgs':allimgsStr,
                        "text" : texts.replace('\\','\pspk1').replace('\pspk1','')
                        }
                myarray = []
                myarray.append(mydict)
                serializedData = json.dumps(myarray)
                #print (serializedData)
                print (newsletterPostUrlsObj.url)

                data_file = open("/tmp/inputfile.json", 'w')
                data_file.write(serializedData)
                data_file.close()
                #Run from same command line directory as code.
                #TODO: Add a code config
                command = "node addDocuments.js blogs /tmp/inputfile.json" 
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
                #if (idx >= 500):
                #    logger.info("Exiting because we reached max index. idx=" + str(idx))
                #    sys.exit(0)
            time.sleep(0.1)
