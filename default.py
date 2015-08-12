#!/usr/bin/env python

import sys
import urllib
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import feedparser


base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
xbmcplugin.setContent(addon_handle, 'plugin.video.category5')
cat5Shows = {}

feedsURL = "http://rss.cat5.tv/"
feedsImage = "http://cdn.zecheriah.com/img/rss/sd/icon-144.jpg"

cat5Shows[0] = {
    'cat5Folder': "Full Episodes HD",
    'cat5Title': "Full Episodes HD",
    'cat5Image': feedsImage,
    'cat5Feed': feedsURL + "hd.rss"

}

cat5Shows[1] = {
    'cat5Folder': "Full Episodes SD",
    'cat5Title': "Full Episodes SD",
    'cat5Image': feedsImage,
    'cat5Feed': feedsURL + "sd.rss"

}

cat5Shows[2] = {
    'cat5Folder': "Full Episodes LD",
    'cat5Title': "Full Episodes LD",
    'cat5Image': feedsImage,
    'cat5Feed': feedsURL + "ld.rss"

}

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

mode = args.get('mode', None)

def addfolders(url, title, image):
    url = build_url({'mode': 'folder', 'foldername': url})
    li = xbmcgui.ListItem(title, iconImage=image)
    return xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

def feedrss(feedrssurl):

    feeds = feedparser.parse( feedrssurl )

    for feed in feeds[ "items" ]:

        url = feed[ "link" ]
        title = feed[ "title" ]
        title = title.replace('Category5 Technology TV - ', '')
        
        image = title.split(' - ')
        image2 = image[0].split('Episode ')
        image3 = "http://cdn3.taliferguson.com/img/tech/" + image2[1] + "/200.jpg"
        
        li = xbmcgui.ListItem(title, iconImage=image3)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

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





