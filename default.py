#!/usr/bin/env python

"""
        Declarations and imports of modules
"""

# import of libraries needed to run Category5.TV video feed
import sys, os, urlparse, xbmc, xbmcgui, xbmcplugin, xbmcaddon, urllib, urllib2,cookielib, re

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

# declares the variable cat5Show to store all the different shows and formats available
cat5Shows = {}

# declares the variable cat5ShowURL for show url list
cat5ShowURL = "http://www.webenguk.com/shows.html"

# declares the variable mode to default to display the folders on load
mode = args.get('mode', None)

# sets a value to the addon_handle for kodi
xbmcplugin.setContent(addon_handle, 'movies')

cat5Settings = xbmcaddon.Addon(id='plugin.video.category5')


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


"""
        Adds folders to Kodi (shows)
"""

def addfolders(url, title, image, qual, quality):
    if int(qual) == quality:
        url = build_url({'mode': 'folder', 'foldername': url})
        li = xbmcgui.ListItem(title, iconImage=image)
        return xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    else:
        return


"""
        Accesses the feed or website as required and downloads the sourcecode
"""

def getURL(url):
    headercode = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
    
    openurl = urllib2.Request(url, headers=headercode)
    response = urllib2.urlopen(openurl)
    source = response.read()

    return source



"""
        Builds the shows list and places it into a dictionary
"""

def shows(showurl):
    sourceCode = getURL(showurl)

    htmlfolder = re.findall(r'<cat5Folder>(.*?)</cat5Folder>', sourceCode)
    htmltitle = re.findall(r'<cat5Title>(.*?)</cat5Title>', sourceCode)
    htmlimage = re.findall(r'<cat5Image>(.*?)</cat5Image>', sourceCode)
    htmlfeed = re.findall(r'<cat5Feed>(.*?)</cat5Feed>', sourceCode)
    htmlqual = re.findall(r'<cat5Quality>(.*?)</cat5Quality>', sourceCode)


    for folderhtml, titlehtml, imagehtml, feedhtml, qualhtml, in zip(htmlfolder, htmltitle, htmlimage, htmlfeed, htmlqual):
        cat5Shows[folderhtml] = {
                    'cat5Folder': folderhtml,
                    'cat5Title': titlehtml,
                    'cat5Image': imagehtml,
                    'cat5Feed': feedhtml,
                    'cat5Quality': qualhtml
        }

    return



"""
        Builds the shows within the folder and display on screen using a list
"""

def feedrss(feedrssurl):
    
    sourceCode = getURL(feedrssurl)
    
    numberrss = re.findall(r'<cat5tv:number>(.*?)</cat5tv:number>', sourceCode)
    titlerss = re.findall(r'<cat5tv:title>(.*?)</cat5tv:title>', sourceCode)
    thumbnailrss = re.findall(r'<cat5tv:thumbnail>(.*?)</cat5tv:thumbnail>', sourceCode)
    descriptionrss = re.findall(r'<cat5tv:description>(.*?)</cat5tv:description>', sourceCode)
    directorrss = re.findall(r'<media:credit role="director">(.*?)</media:credit>', sourceCode)
    writerrss = re.findall(r'<author>(.*?)</author>', sourceCode)
    durationrss = re.findall(r'<itunes:duration>(.*?)</itunes:duration>', sourceCode)
    linksrss = re.findall(r'<link>(.*?).m4v</link>', sourceCode)
    if len(linksrss) <= 0:
        linksrss = re.findall(r'<link>(.*?).mp3</link>', sourceCode)
    
    for rssnumber, rsstitle, rssthumbnail, rsslinks, rssdescription, rrsdirector, rsswriter, rssduration in zip(numberrss, titlerss, thumbnailrss, linksrss, descriptionrss, directorrss, writerrss, durationrss):
        
        url = rsslinks
        title = rssnumber + ' - ' + rsstitle
        
        li = xbmcgui.ListItem(title, iconImage=rssthumbnail)
        li.setInfo('video', { 'title': rsstitle,
                              'episode': rssnumber,
                              'plot': rssdescription,
                              'director': rrsdirector,
                              'writer': rsswriter
                            })
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)


    return xbmcplugin.endOfDirectory(addon_handle)



"""
        Main application
"""

# Gathers the quality setting for the video
quality = int(cat5Settings.getSetting("video_quality"))

# Gathers all the show folders ready for populating
shows(cat5ShowURL)

# checks mode variable to see which state it is set to
if mode is None:
    
    # live feed for Category5.TV
    url = ''
    li = xbmcgui.ListItem('Live Stream (coming soon)')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    
    # loops through each of the shows and displays in a folder format on Kodi
    for cat5Folders, data in cat5Shows.iteritems():
        addfolders(data['cat5Folder'], data['cat5Title'], data['cat5Image'], data['cat5Quality'], quality)

    # closes the display process and instructs Kodi to wait for user input
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'folder':
    # selects the folder name the user has chosen
    foldername = args['foldername'][0]
    
    # searches the select folder name
    for cat5Folders, data in cat5Shows.iteritems():
        
        # checks to see if the folder name exisits at the point of the loop
        if data['cat5Folder'] == foldername:
            
            # sends information to be added of each show to be compiled and displayed
            feedrss(data['cat5Feed'])
            
            # stops the loop
            break




