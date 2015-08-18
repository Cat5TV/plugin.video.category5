#!/usr/bin/env python

"""
        Declarations and imports of modules
"""

# import of libraries needed to run Category5.TV video feed
import sys, os, urlparse, xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs, urllib, urllib2,cookielib, re, json, time

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

addon = xbmcaddon.Addon()

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


"""
        Adds folders to Kodi (shows)
"""

def addfolders(url, title, image, qual, quality):
    
    # Checks the quality setting for the user and matches the correct shows to it
    if int(qual) == quality:
        
        # builds the url(internal only) for kodi to be able to call
        url = build_url({'mode': 'folder', 'foldername': url})
        
        # adds a list item to include the folder image and title
        li = xbmcgui.ListItem(title, iconImage=image)
        
        my_addon = xbmcaddon.Addon('plugin.video.category5')
        
        li.setThumbnailImage(image)
        li.setProperty('fanart_image', my_addon.getAddonInfo('fanart'))
        
        # sets the url and list item inside kodi and returns the result
        return xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    
    else:

        # if no quality is set it will return nothing
        return


"""
        Accesses the feed or website as required and downloads the sourcecode
"""

def getURL(url):
    
    # sets the header for any website.  This will instuct any webserver the request is set to mozilla
    headercode = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

    # opens up a link to the webserver and requests the webpage to see if vailid
    openurl = urllib2.Request(url, headers=headercode)

    # opens a connection  to the webpage
    response = urllib2.urlopen(openurl)

    # reads all the sourcecode of the webpage
    source = response.read()

    # returns the source code
    return source



"""
        Builds the shows list and places it into a dictionary (dynamic adding of shows)
"""

def shows(showurl):
    
    # requests the sourcecode for a webpage
    sourceCode = getURL(showurl)

    # searches the sourcecode and gets anything between the cat5Folder tags and places it into the variable htmlfolder
    htmlfolder = re.findall(r'<cat5Folder>(.*?)</cat5Folder>', sourceCode)
    
    # searches the sourcecode and gets anything between the cat5Title tags and places it into the variable htmltitle
    htmltitle = re.findall(r'<cat5Title>(.*?)</cat5Title>', sourceCode)
    
    # searches the sourcecode and gets anything between the cat5Image tags and places it into the variable htmlimage
    htmlimage = re.findall(r'<cat5Image>(.*?)</cat5Image>', sourceCode)
    
    # searches the sourcecode and gets anything between the cat5Feed tags and places it into the variable htmlfeed
    htmlfeed = re.findall(r'<cat5Feed>(.*?)</cat5Feed>', sourceCode)
    
    # searches the sourcecode and gets anything between the cat5Quality tags and places it into the variable htmlqual
    htmlqual = re.findall(r'<cat5Quality>(.*?)</cat5Quality>', sourceCode)

    # loops through all data found from htmlfolder, htmltitle, htmltitle, htmlfeed, htmlqual and adds information to variable (dirctory) cat5Shows
    for folderhtml, titlehtml, imagehtml, feedhtml, qualhtml, in zip(htmlfolder, htmltitle, htmlimage, htmlfeed, htmlqual):
        cat5Shows[folderhtml] = {
                    'cat5Folder': folderhtml,
                    'cat5Title': titlehtml,
                    'cat5Image': imagehtml,
                    'cat5Feed': feedhtml,
                    'cat5Quality': qualhtml
        }

    # returns back to the running code
    return



"""
        Builds the shows within the folder and display on screen using a list
"""

def feedrss(feedrssurl):
    
    # requests the sourcecode for a webpage
    sourceCode = getURL(feedrssurl)
    
    # searches the sourcecode and gets anything between the cat5tv:number tags and places it into the variable numberrss
    numberrss = re.findall(r'<cat5tv:number>(.*?)</cat5tv:number>', sourceCode)
    
    # searches the sourcecode and gets anything between the cat5tv:title tags and places it into the variable titlerss
    titlerss = re.findall(r'<cat5tv:title>(.*?)</cat5tv:title>', sourceCode)
    
    # searches the sourcecode and gets anything between the cat5tv:thumbnail tags and places it into the variable thumbnailrss
    thumbnailrss = re.findall(r'<cat5tv:thumbnail>(.*?)</cat5tv:thumbnail>', sourceCode)
    
    # searches the sourcecode and gets anything between the cat5tv:description tags and places it into the variable descriptionrss
    descriptionrss = re.findall(r'<cat5tv:description>(.*?)</cat5tv:description>', sourceCode)
    
    # searches the sourcecode and gets anything between the media:credit role="director" tags and places it into the variable directorrss
    directorrss = re.findall(r'<media:credit role="director">(.*?)</media:credit>', sourceCode)
    
    # searches the sourcecode and gets anything between the author tags and places it into the variable writerrss
    writerrss = re.findall(r'<author>(.*?)</author>', sourceCode)
    
    # searches the sourcecode and gets anything between the itunes:duration tags and places it into the variable durationrss
    durationrss = re.findall(r'<itunes:duration>(.*?)</itunes:duration>', sourceCode)

    # searches the sourcecode and gets anything between the link tags and places it into the variable linksrss (m4v)
    linksrss = re.findall(r'<link>(.*?).m4v</link>', sourceCode)
    
    # checks to make sure linkrss has content for m4v if not check for mp3
    if len(linksrss) <= 0:
        
        # searches the sourcecode and gets anything between the link tags and places it into the variable linksrss (mp3)
        linksrss = re.findall(r'<link>(.*?).mp3</link>', sourceCode)
    
    # loops through all data found from numberrss, titlerss, thumbnailrss, descriptionrss, directorrss, writerrss, durationrss, linksrss and adds information to list item
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

        li.setThumbnailImage(rssthumbnail)
        li.setProperty('fanart_image', rssthumbnail)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)


    return xbmcplugin.endOfDirectory(addon_handle)

def set_view_mode(view_mode_id):
    xbmc.executebuiltin('Container.SetViewMode(%d)' % int(view_mode_id))

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
    url = 'rtsp://mediapanel.siglocero.net/8082/8082'
    li = xbmcgui.ListItem('Live Stream - image to come soon')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    
    # loops through each of the shows and displays in a folder format on Kodi
    for cat5Folders, data in cat5Shows.iteritems():
        addfolders(data['cat5Folder'], data['cat5Title'], data['cat5Image'], data['cat5Quality'], quality)
    
    # closes the display process and instructs Kodi to wait for user input
    xbmcplugin.endOfDirectory(addon_handle)

    set_view_mode('500')

elif mode[0] == 'folder':
    # selects the folder name the user has chosen
    foldername = args['foldername'][0]
    
    # searches the select folder name
    for cat5Folders, data in cat5Shows.iteritems():
        
        # checks to see if the folder name exisits at the point of the loop
        if data['cat5Folder'] == foldername:
            
            # sends information to be added of each show to be compiled and displayed
            feedrss(data['cat5Feed'])
            set_view_mode('504')
            # stops the loop
            break
