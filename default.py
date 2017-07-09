#!/usr/bin/env python

"""
        Declarations and imports of modules
"""

# import of libraries needed to run Category5.TV video feed
import sys, os, urlparse, xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs, urllib, urllib2, cookielib, re, json, time
import datetime, string, zlib, HTMLParser, httplib

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

# declares the variable cat5Show to store all the different shows and formats available
cat5Shows = {}

# declares the variable cat5Live to store all the different live shows and formats available
cat5Live = {}

# declares the variable cat5ShowURL for show url list
cat5ShowURL = "http://rss.cat5.tv/kodi/shows.php"

# sets a value to the addon_handle for kodi
xbmcplugin.setContent(addon_handle, 'movies')

cat5Settings = xbmcaddon.Addon(id='plugin.video.category5')

# declares the variable addon for the category5 plugin
addon = xbmcaddon.Addon()

"""
        Adds folder URL configurations and links
"""
def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


"""
        Adds folders to Kodi (shows)
"""

def addfolders(url, title, image, qual, quality, modes):
    
    # Checks the quality setting for the user and matches the correct shows to it
    if int(qual) == quality:
        
        # builds the url(internal only) for kodi to be able to call
        url = build_url({'mode': modes, 'foldername': url, 'title': title})
        
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

    # load the list of available feeds from the Cat5 backend
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
    Builds the live shows within the folder and display on screen using a list
    
"""

def liveshows(showurl):
    
    # requests the sourcecode for a webpage
    sourceCode = getURL(showurl)
    
    # searches the sourcecode and gets anything between the livetitle tags and places it into the variable livetitle
    livetitle = re.findall(r'<liveTitle>(.*?)</liveTitle>', sourceCode)

    
    # searches the sourcecode and gets anything between the liveImage tags and places it into the variable liveimage
    liveimage = re.findall(r'<liveImage>(.*?)</liveImage>', sourceCode)

    
    # searches the sourcecode and gets anything between the liveFeed tags and places it into the variable livefeed
    livefeed = re.findall(r'<liveFeed>(.*?)</liveFeed>', sourceCode)
    
    # loops through all data found from livetitle, liveimage, livefeed and adds information to variable (dirctory) cat5Shows
    for titlelive, imagelive, feedlive in zip(livetitle, liveimage, livefeed):
        cat5Live[titlelive] = {
            'cat5Title': titlelive,
            'cat5Image': imagelive,
            'cat5Feed': feedlive
    }

    # returns back to the running code
    return

"""
        Builds the shows within the folder and display on screen using a list
"""

def feedrss(sourceCode, seasons):
    
    xbmcplugin.setContent(int(sys.argv[1]), 'shows')
    xbmcplugin.addSortMethod(int(sys.argv[1]),xbmcplugin.SORT_METHOD_EPISODE)

    # removes all new lines or character returns from the source code
    sourceCode1 = sourceCode.replace('\n', ' ').replace('\r', '')

    # searches the sourcecode and gets anything between the cat5tv:number tags and places it into the variable numberrss
    numberrss = re.findall(r'<cat5tv:number>(.*?)</cat5tv:number>', sourceCode)

    # searches the sourcecode and gets anything between the cat5tv:title tags and places it into the variable titlerss
    titlerss = re.findall(r'<cat5tv:title>(.*?)</cat5tv:title>', sourceCode)
    
    # searches the sourcecode and gets anything between the cat5tv:year tags and places it into the variable yearrss
    yearrss = re.findall(r'<cat5tv:year>(.*?)</cat5tv:year>', sourceCode)
    
    # searches the sourcecode and gets anything between the cat5tv:genre tags and places it into the variable genrerss
    genrerss = re.findall(r'<cat5tv:genre>(.*?)</cat5tv:genre>', sourceCode)
    
    # searches the sourcecode and gets anything between the cat5tv:description tags and places it into the variable descriptionrss
    descriptionrss = re.findall(r'<cat5tv:description>(.*?)</cat5tv:description>', sourceCode1)
    
    # searches the sourcecode and gets anything between the cat5tv:thumbnail tags and places it into the variable thumbnailrss
    thumbnailrss = re.findall(r'<cat5tv:thumbnail>(.*?)</cat5tv:thumbnail>', sourceCode)
    
    # searches the sourcecode and gets anything between the media:credit role="director" tags and places it into the variable directorrss
    directorrss = re.findall(r'<media:credit role="director">(.*?)</media:credit>', sourceCode)
    
    # searches the sourcecode and gets anything between the author tags and places it into the variable writerrss
    seasonrss = re.findall(r'<cat5tv:season>(.*?)</cat5tv:season>', sourceCode)

    # searches the sourcecode and gets anything between the author tags and places it into the variable writerrss
    writerrss = re.findall(r'<author>(.*?)</author>', sourceCode)

    # searches the sourcecode and gets anything between the link tags and places it into the variable linksrss (m4v)
    linksrss = re.findall(r'<link>(.*?).m4v</link>', sourceCode)
    
    # checks to make sure linkrss has content for m4v if not check for mp3
    if len(linksrss) <= 0:
        
        # searches the sourcecode and gets anything between the link tags and places it into the variable linksrss (mp3)
        linksrss = re.findall(r'<link>(.*?).mp3</link>', sourceCode)

    # loops through all data found from numberrss, titlerss, thumbnailrss and adds information to list item
    for rssnumber, rsstitle, rssyear, rssgenre, rssdescription, rssdirector, rssthumbnail, rsslinks, rsswriter, rssseason in zip(numberrss, titlerss, yearrss, genrerss, descriptionrss, directorrss, thumbnailrss, linksrss, writerrss, seasonrss):
        
        if rssseason == seasons:
            url = rsslinks
            rsstitle = rssnumber + ' - ' + rsstitle
        
            li = xbmcgui.ListItem(title, iconImage=rssthumbnail)
            li.setInfo('video', {
                                #'episode': rssnumber,
                                'title': rsstitle,
                                'year': rssyear,
                                'genre': rssgenre,
                                'plot': rssdescription,
                                'director': rssdirector,
                                'writer': rsswriter
                       })

            li.setThumbnailImage(rssthumbnail)
            li.setProperty('fanart_image', rssthumbnail)
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)


    return xbmcplugin.endOfDirectory(int(sys.argv[1]))

"""
    Builds the shows within the folder and display on screen using a list
"""

def seasonrss(sourceCode):
    
    # searches the sourcecode and gets anything between the cat5tv:season tags and places it into the variable seasonheader
    seasonheader = re.findall(r'<cat5tv:season>(.*?)</cat5tv:season>', sourceCode)
    
    seasons = seasonheader[0]

    return seasons

def set_view_mode(view_mode_id):
    xbmc.executebuiltin('Container.SetViewMode(%d)' % int(view_mode_id))

def getLastEpisodeImage(sourceCode, season):
    thumbnailrss = re.findall(r'<cat5tv:thumbnail>(.*?)</cat5tv:thumbnail>', sourceCode)
    seasonrss = re.findall(r'<cat5tv:season>(.*?)</cat5tv:season>', sourceCode)
    
    for rssthumbnail, rssseason in zip(thumbnailrss, seasonrss):
        
        if rssseason == season:
            return rssthumbnail
            break


"""
        Main application
"""

# Gathers the quality setting for the video
quality = int(cat5Settings.getSetting("video_quality"))

# Gathers all the show folders ready for populating
shows(cat5ShowURL)

liveshows(cat5ShowURL)


parms = {}
try:
    parms = dict( arg.split( "=" ) for arg in ((sys.argv[2][1:]).split( "&" )) )
    for key in parms:
        try:    parms[key] = urllib.unquote_plus(parms[key]).decode(UTF8)
        except: pass
except:
    parms = {}

p = parms.get

mode = p('mode',None)


# checks mode variable to see which state it is set to
if mode == None:
    
    xbmcplugin.setContent(int(sys.argv[1]), 'shows')
    xbmcplugin.addSortMethod(int(sys.argv[1]),xbmcplugin.SORT_METHOD_EPISODE)
    
    # live feed for Category5.TV
    for cat5Titles, data in cat5Live.iteritems():
        url = data['cat5Feed']
        li = xbmcgui.ListItem(data['cat5Title'], iconImage=data['cat5Image'])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    
    # loops through each of the shows and displays in a folder format on Kodi
    for cat5Folders, data in cat5Shows.iteritems():
        addfolders(data['cat5Folder'], data['cat5Title'], data['cat5Image'], data['cat5Quality'], quality, 'GS')
    
    # closes the display process and instructs Kodi to wait for user input
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

    set_view_mode('500')

elif mode == 'FS':
    # selects the folder name the user has chosen
    foldername = args['foldername'][0]
    # selects the Season the user has chosen
    titleTemp = args['title'][0]
    
    # gathers the numbers within the title "Season"
    titleTemp = re.findall('\d+', titleTemp)
    
    # sets the title variable to the number of the season
    title = titleTemp[0]
    
    # searches the select folder name
    for cat5Folders, data in cat5Shows.iteritems():
        
        # checks to see if the folder name exisits at the point of the loop
        if data['cat5Folder'] == foldername:
            sourcecode = getURL(data['cat5Feed'])
            feedrss(sourcecode, title)
            set_view_mode('504')
            break

elif mode == 'GS':
    # selects the folder name the user has chosen
    foldername = args['foldername'][0]
    
    # searches the select folder name
    for cat5Folders, data in cat5Shows.iteritems():
        if data['cat5Folder'] == foldername:
            sourcecode = getURL(data['cat5Feed'])
            seasons = seasonrss(sourcecode)
            xbmcplugin.setContent(int(sys.argv[1]), 'shows')
            xbmcplugin.addSortMethod(int(sys.argv[1]),xbmcplugin.SORT_METHOD_EPISODE)
            for x in range (int(seasons), 0, -1):
                addfolders(data['cat5Folder'], "Season %s" % str(x), getLastEpisodeImage(sourcecode, str(x)), data['cat5Quality'], quality, 'FS')
            set_view_mode('500')
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            break
