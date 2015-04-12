# -*- coding: utf-8 -*-
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
iZap4u unofficial add-on
Author:     WPierre
"""

import os, re, xbmcplugin, xbmcgui, xbmcaddon, urllib, urllib2, sys, cookielib, pickle, datetime, time
from BeautifulSoup import BeautifulSoup
import json, urllib2, HTMLParser
from collections import OrderedDict
import os
from os.path import basename
"""
Class used as a C-struct to store video informations
"""
class videoInfo:
    pass

"""
Class used to report login error
"""
class loginExpcetion(Exception):
    pass

# Global variable definition
## Header for every log in this plugin
pluginLogHeader = "[KODI_iZap4u] "

## Values for the mode parameter
MODE_LAST_SHOWS, MODE_CATEGORIES, MODE_SEARCH, MODE_SHOW_BY_URL, MODE_LINKS = range(5)
MODE_ZAPS_LIST = 1
MODE_10SEQUENCES_LIST = 2
MODE_ZAP_QUALITY = 3
MODE_10SEQUENCES_QUALITY = 4
MODE_SEARCH = 5

settings  = xbmcaddon.Addon(id='plugin.video.izap4u')
website_url = "http://www.izap4u.com"
#url = izap4uapi_url
name      = 'iZap4u Kodi'
mode      = None
version   = settings.getAddonInfo('version')
language = settings.getLocalizedString
fanartimage = os.path.join(settings.getAddonInfo("path"), "izap4u_background.jpg")



def requestinput():
    """Request input from user
        
    Uses the XBMC's keyboard to get a string
    """
    kbd = xbmc.Keyboard('default', 'heading', True)
    kbd.setDefault('')
    kbd.setHeading('Recherche')
    kbd.setHiddenInput(False)
    kbd.doModal()
    if (kbd.isConfirmed()):
        name_confirmed  = kbd.getText()
        return name_confirmed
    else:
        return 'Null'

def Error_message(message):
    dialog = xbmcgui.Dialog()
    dialog.ok(unicode(language(30023)), unicode(language(message)))

def getZaps():
    xbmc.log(msg=pluginLogHeader + "Getting zaps",level=xbmc.LOGDEBUG)
    settings = xbmcaddon.Addon(id='plugin.video.izap4u')

    try:
        server_url = urllib2.urlopen(website_url)
        soup = BeautifulSoup(server_url.read())
        #xbmc.log(msg=pluginLogHeader + "Soup:"+soup.prettify(),level=xbmc.LOGDEBUG)

        server_url.close()
        liens = soup.findAll('a',{"class":'thumbzap'})
    except:
        Error_message(30017)
        xbmc.log(msg=pluginLogHeader + 'Exception (init): ' + str(sys.exc_info()),level=xbmc.LOGFATAL)
        return
    for video in liens:
        if video['href'].find("/zap/") != -1:
            add_dir(video['title'],video['href'], MODE_ZAP_QUALITY,video.find('img')['data-original'])

def getZapQualities(url):
    xbmc.log(msg=pluginLogHeader + "Getting qualities for zap "+url,level=xbmc.LOGDEBUG)

    server_url = urllib2.urlopen(url)
    html = server_url.read()
    liens = re.findall(r'file: "(.*\.mp4)"', html)
    liens = list(set(liens))
    try:
        for video in liens:
            addlink(video)
    except:
        Error_message(30017)
        xbmc.log(msg=pluginLogHeader + 'Exception (init): ' + str(sys.exc_info()),level=xbmc.LOGFATAL)
        return

def get10Sequences():
    xbmc.log(msg=pluginLogHeader + "Getting zaps",level=xbmc.LOGDEBUG)
    settings = xbmcaddon.Addon(id='plugin.video.izap4u')

    try:
        server_url = urllib2.urlopen(website_url)
        soup = BeautifulSoup(server_url.read())
        #xbmc.log(msg=pluginLogHeader + "Soup:"+soup.prettify(),level=xbmc.LOGDEBUG)

        server_url.close()
        liens = soup.findAll('a',{"class":'thumbzap'})
    except:
        Error_message(30017)
        xbmc.log(msg=pluginLogHeader + 'Exception (init): ' + str(sys.exc_info()),level=xbmc.LOGFATAL)
        return
    for video in liens:
        if video['href'].find("/10sequences/") != -1:
            add_dir(video['title'],video['href'], MODE_10SEQUENCES_QUALITY,video.find('img')['data-original'])

def get10SequencesQualities(url):
    xbmc.log(msg=pluginLogHeader + "Getting qualities for zap "+url,level=xbmc.LOGDEBUG)

    server_url = urllib2.urlopen(url)
    html = server_url.read()
    liens = re.findall(r'file: "(.*\.mp4)"', html)
    liens = list(set(liens))
    try:
        for video in liens:
            addlink(video)
    except:
        Error_message(30017)
        xbmc.log(msg=pluginLogHeader + 'Exception (init): ' + str(sys.exc_info()),level=xbmc.LOGFATAL)
        return


def initialIndex():
    """Creates initial index
    
    Create the initial menu with the right identification values for the add-on to know which option have been selected
    """
    add_dir(unicode(language(30001)), '', MODE_ZAPS_LIST, '')
    add_dir(unicode(language(30003)), '', MODE_10SEQUENCES_LIST, '')


def get_params():
    """
    Get parameters
    """
    param       = []
    paramstring = sys.argv[2]

    if len(paramstring) >= 2:
        params        = sys.argv[2]
        cleanedparams = params.replace('?','')

        if (params[len(params)-1] == '/'):
            params = params[0:len(params)-2]

        pairsofparams = cleanedparams.split('&')
        param = {}

        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param

def addlink(url):
    xbmc.log(msg=pluginLogHeader + "Added video link "+url,level=xbmc.LOGDEBUG)
    liz = xbmcgui.ListItem(url)
    liz.setInfo(
                 type="Video",
                 infoLabels={ "title": urllib2.unquote(os.path.splitext(basename(url))[0]),
                              "playcount": int(0)
                            }
               )
    liz.setProperty("IsPlayable","true")
    liz.setProperty("mimetype","video/mp4")

    ok  = xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]),
                                       url=url,
                                       listitem=liz,
                                       isFolder=False )
    return ok

def add_dir(name, url, mode, iconimage):
    """
    Adds a directory to the list
    """
    ok  = True
    
    # Hack to avoid incompatiblity of urllib with unicode string
    if isinstance(name, str):
        url = sys.argv[0]+"?url="+urllib.quote_plus(url)+\
            "&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    else:
        url = sys.argv[0]+"?url="+urllib.quote_plus(url)+\
        "&mode="+str(mode)+"&name="+urllib.quote_plus(name.encode("ascii", "ignore"))
    showid = url.split('?')[1].split('&')[0].split('=')[1]
    thumbnailimage = os.path.join(settings.getAddonInfo("path"), 'resources', 'images', showid + '.jpeg')
    if not iconimage == '':
        liz = xbmcgui.ListItem(name,
                               iconImage=iconimage,
                               thumbnailImage=iconimage)
    else:
        liz = xbmcgui.ListItem(name,
                               iconImage=thumbnailimage,
                               thumbnailImage=thumbnailimage)
    try:
        liz.setProperty("fanart_image",iconimage)
    except:
        fanartimage_temp = None
    liz.setInfo( 
                 type="Video", 
                 infoLabels={ "Title": name } 
               )
    ok  = xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]),
                                       url=url, 
                                       listitem=liz, 
                                       isFolder=True )
    return ok

## Start of the add-on
xbmc.log(msg=pluginLogHeader + "-----------------------",level=xbmc.LOGDEBUG)
xbmc.log(msg=pluginLogHeader + "iZap4u plugin main loop",level=xbmc.LOGDEBUG)
pluginHandle = int(sys.argv[1])

## Reading parameters given to the add-on
params = get_params()
xbmc.log(msg=pluginLogHeader + "Parameters read",level=xbmc.LOGDEBUG)

try:
    url = urllib.unquote_plus(params["url"])
except:
    url = ""
try:
    mode = int(params["mode"])
except:
    pass
try:
    _id = int(params["id"])
except:
    _id = 0
xbmcplugin.setContent 	(pluginHandle,"movies")
xbmc.log(msg=pluginLogHeader + "requested mode : " + str(mode),level=xbmc.LOGDEBUG)
xbmc.log(msg=pluginLogHeader + "requested url : " + url,level=xbmc.LOGDEBUG)
xbmc.log(msg=pluginLogHeader + "requested id : " + str(_id),level=xbmc.LOGDEBUG)

requestHandler = urllib2.build_opener()





# Determining and executing action
if( mode == None or url == None ) and _id == 0:
    xbmc.log(msg=pluginLogHeader + "Loading initial index",level=xbmc.LOGDEBUG)
    initialIndex()
elif mode == MODE_ZAPS_LIST and _id == 0:
    xbmc.log(msg=pluginLogHeader + "Retrieving zap list",level=xbmc.LOGDEBUG)
    getZaps()
elif mode == MODE_ZAP_QUALITY and _id == 0:
    xbmc.log(msg=pluginLogHeader + "Retrieving zap video quality",level=xbmc.LOGDEBUG)
    getZapQualities(url)
elif mode == MODE_10SEQUENCES_LIST and _id == 0:
    xbmc.log(msg=pluginLogHeader + "Retrieving 10sequences list",level=xbmc.LOGDEBUG)
    get10Sequences()
elif mode == MODE_10SEQUENCES_QUALITY and _id == 0:
    xbmc.log(msg=pluginLogHeader + "Retrieving 10sequences video quality",level=xbmc.LOGDEBUG)
    get10SequencesQualities(url)

#xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
#xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
