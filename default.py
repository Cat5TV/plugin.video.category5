#!/usr/bin/env python

import sys
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import urllib
import urllib2,cookielib
import re

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
xbmcplugin.setContent(addon_handle, 'plugin.video.category5')
cat5Shows = {}

feedsImage = "http://cdn.zecheriah.com/img/rss/sd/icon-144.jpg"

cat5Shows[0] = {
    'cat5Folder': "Full Episodes HD",
    'cat5Title': "Full Episodes HD",
    'cat5Image': feedsImage,
    'cat5Feed': "http://rss.cat5.tv/kodi/tech-hd.rss"
}

cat5Shows[1] = {
    'cat5Folder': "Full Episodes SD",
    'cat5Title': "Full Episodes SD",
    'cat5Image': feedsImage,
    'cat5Feed': "http://rss.cat5.tv/kodi/tech-sd.rss"
}

cat5Shows[2] = {
    'cat5Folder': "Full Episodes LD",
    'cat5Title': "Full Episodes LD",
    'cat5Image': feedsImage,
    'cat5Feed': "http://rss.cat5.tv/kodi/tech-ld.rss"
}

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

mode = args.get('mode', None)

def addfolders(url, title, image):
    url = build_url({'mode': 'folder', 'foldername': url})
    li = xbmcgui.ListItem(title, iconImage=image)
    return xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

def feedrss(feedrssurl):
    
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
    
    rssurl = urllib2.Request(feedrssurl, headers=hdr)
    response = urllib2.urlopen(rssurl)
    
    sourceCode = response.read()
    
    numberrss = re.findall(r'<cat5tv:number>(.*?)</cat5tv:number>', sourceCode)
    titlerss = re.findall(r'<cat5tv:title>(.*?)</cat5tv:title>', sourceCode)
    thumbnailrss = re.findall(r'<cat5tv:thumbnail>(.*?)</cat5tv:thumbnail>', sourceCode)
    linksrss = re.findall(r'<link>(.*?).m4v</link>', sourceCode)
    descriptionrss = re.findall(r'<cat5tv:description>(.*?)</cat5tv:description>', sourceCode)

    for rssnumber, rsstitle, rssthumbnail, rsslinks, rssdescription in zip(numberrss, titlerss, thumbnailrss, linksrss, descriptionrss):
        
        url = rsslinks
        title = rssnumber + ' - ' + rsstitle
        
        li = xbmcgui.ListItem(title, iconImage=rssthumbnail)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)


    return xbmcplugin.endOfDirectory(addon_handle)

if mode is None:
    url = ''
    li = xbmcgui.ListItem('Live Stream (coming soon)')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    
    for cat5Folders, data in cat5Shows.iteritems():
        addfolders(data['cat5Folder'], data['cat5Title'], data['cat5Image'])

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'folder':
    foldername = args['foldername'][0]
    for cat5Folders, data in cat5Shows.iteritems():
        if data['cat5Folder'] == foldername:
            feedrss(data['cat5Feed'])





