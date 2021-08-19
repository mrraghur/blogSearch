# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.db import models
# Create your models here.
class substacknewsletter(models.Model):
    url = models.TextField(unique=True)
    def __str__(self):
        return "id:" + str(self.id) + "~" + "url:" + str(self.url)

#A sitemap could come from www.example.com/sitemap.xml or from parsing another sitemap.xml
class sitemap(models.Model):
    text = models.TextField() #text of the sitemap.xml file. This test is usually in xml format
    parentnewsletter = models.ForeignKey(
            substacknewsletter,
            on_delete=models.SET_NULL,
            null=True); #No need to delete a sitemap just because parent is deleted.
    #If this was derived from a different sitemap, then parentSiteMap is non null
    parentSiteMap =models.TextField(null=True) 
    parentType = models.TextField()   #ideally should use enum field, but too lazy.
                                      #For now, values are newsletter or sitemap
    def __str__(self):
        return "id:" + str(self.id) + "~" + "parentnewsletter=" + str(self.parentnewsletter)
        +"parentSiteMap=" + self.parentSiteMap + "~" + "parentType=" + self.parentType
    
    
#Aboutme page of a blog.
class aboutme(models.Model):
    text = models.TextField() #text of the about me page.
    url = models.TextField(unique=True)
    parentnewsletter = models.ForeignKey(
            substacknewsletter,
            on_delete=models.SET_NULL,
            null=True); #No need to delete an aboutme page just because parent is deleted.
    def __str__(self):
        return "id:" + str(self.id) + "~" + "parentnewsletter=" + str(self.parentnewsletter)
        +"url=" + self.url
        +"text=" + self.text
 


class newsletterPostUrls(models.Model):
    url = models.TextField(unique=True)
    origtext = models.TextField(null=True)
    parentnewsletter = models.ForeignKey(
      substacknewsletter,
      on_delete=models.CASCADE,  #when parent newsletter is deleted, this post can also be deleted.
      null=True
    )

    def __str__(self):
        return "id:" + str(self.id) + "~" + "parentnewsletter:" + ("none" if (self.parentnewsletter == None) else str(self.parentnewsletter)) + "~" + "url:" + str(self.url)

class postsToIgnore(models.Model):
    url = models.TextField(unique=True)
    countOfTriesSoFar = models.IntegerField(null=False, default=0)
    errMsg = models.TextField(unique=False,null=True)

    def __str__(self):
        return "url:" + url + "~" + "countOfTriesSoFar:" + str(self.countOfTriesSoFar) + "~"  + "errMsg:" + self.errMsg

class newsletterscrapestatus(models.Model):
    downloadedsitemap = models.BooleanField(False)
    generatedAllPostUrls = models.BooleanField(False)
    #postsyettobedownloaded = models.TextField() #'|' seperated strings.
    def __str__(self):
        return "id:" + str(self.id) + "~" + "downloadedsitemap:" + downloadedsitemap + "~" + "generatedAllPostUrls:" + generatedAllPostUrls
    





