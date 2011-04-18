# PMS plugin framework
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

####################################################################################################

MUSIC_PREFIX = "/music/sverigesradioplay"

NAME = L('Title')

# make sure to replace artwork with what you want
# these filenames reference the example files in
# the Contents/Resources/ folder in the bundle
ART           = 'art-default.png'
ICON          = 'icon-default.png'

ITUNES_NAMESPACE                      = {'itunes':'http://www.itunes.com/dtds/podcast-1.0.dtd'}

####################################################################################################

def Start():

    ## make this plugin show up in the 'Music' section
    ## in Plex. The L() function pulls the string out of the strings
    ## file in the Contents/Strings/ folder in the bundle
    ## see also:
    ##  http://dev.plexapp.com/docs/mod_Plugin.html
    ##  http://dev.plexapp.com/docs/Bundle.html#the-strings-directory
    Plugin.AddPrefixHandler(MUSIC_PREFIX, MainMenu, L('MainTitle'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    ## set some defaults so that you don't have to
    ## pass these parameters to these object types
    ## every single time
    ## see also:
    ##  http://dev.plexapp.com/docs/Objects.html
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)
    DirectoryItem.summary = L("Summary")

  


#### the rest of these are user created functions and
#### are not reserved by the plugin framework.
#### see: http://dev.plexapp.com/docs/Functions.html for
#### a list of reserved functions above



#
# Example main menu referenced in the Start() method
# for the 'Music' prefix handler
#

def MainMenu():

    # Container acting sort of like a folder on
    # a file system containing other things like
    # "sub-folders", videos, music, etc
    # see:
    #  http://dev.plexapp.com/docs/Objects.html#MediaContainer
    dir = MediaContainer(viewGroup="List")


    #  Add ListenLiveMenu
    dir.Append(
        Function(
            DirectoryItem(
                ListenLiveMenu,
                L("ListenLiveTitle"),
                subtitle=L("ListenLiveSubtitle"),
                summary=L("ListenLiveSummary"),
                thumb=R(ICON),
                art=R(ART)
            )
        )
    )

    #  Add AllProgramsMenu
    dir.Append(
        Function(
            DirectoryItem(
                AllProgramsMenu,
                L("AllProgramsTitle"),
                subtitle=L("AllProgramsSubtitle"),
                summary=L("AllProgramsSummary"),
                thumb=R(ICON),
                art=R(ART)
            ),
            categoryid=0,
            categorytitle=L("AllProgramsTitle")
        )
    )

    #  Add Categories
    page = XML.ElementFromURL("http://api.sr.se/api/Poddradio/PoddCategories.aspx")

    for item in page.getiterator('item'):
   
        dir.Append(
            Function(
                DirectoryItem(
                    AllProgramsMenu,
                    item.findtext("title"),
                    subtitle="",
                    summary="",
                    thumb=R(ICON),
                    art=R(ART)
                ),
                categoryid=int(item.findtext("id", default="0")),
                categorytitle=item.findtext("title")
            )
        )


    # ... and then return the container
    return dir

def ListenLiveMenu(sender):

    ## you might want to try making me return a MediaContainer
    ## containing a list of DirectoryItems to see what happens =)

    dir = MediaContainer(viewGroup="InfoList")
    dir.title2 = L("ListenLiveTitle")

    page = XML.ElementFromURL("http://api.sr.se/api/channels/channels.aspx")
    rightnow = XML.ElementFromURL("http://api.sr.se/api/rightnowinfo/rightnowinfo.aspx?filterinfo=all")

    for channel in page.getiterator('channel'):

        info = rightnow.find("Channel[@Id='" + channel.attrib.get("id") + "']")
        desc = ""

        if info:

            if info.findtext("ProgramTitle"):
                desc += str(info.findtext("ProgramTitle")) + "\n"
                if info.findtext("ProgramInfo"):
                    desc += str(info.findtext("ProgramInfo")) + "\n\n"
                else:
                    desc += "\n"
            else:
                if info.findtext("Song"):
                    desc += str(info.findtext("Song")) + "\n\n"
                if info.findtext("NextSong"):
                    desc += L("NextProgram") + ":\n" + str(info.findtext("NextSong")) + "\n\n"

            if info.findtext("NextProgramStartTime"):
                desc += "\n" + L("NextProgram") + ":\n"
                if info.findtext("NextProgramTitle"):
                    desc += str(info.findtext("NextProgramTitle")) + " (" + str(info.findtext("NextProgramStartTime")) + ")\n"
                    if info.findtext("NextProgramDescription"):
                        desc += str(info.findtext("NextProgramDescription")) + "\n"

        dir.Append(
            TrackItem(
                channel.findtext("streamingurl/url[@type='mp3']"),
                channel.attrib.get("name"),
                subtitle=channel.findtext("tagline"),
                summary=desc,
                thumb=channel.findtext("logo")
            )
        )


    # ... and then return the container
    return dir
  
def AllProgramsMenu(sender, categoryid, categorytitle):

    dir = MediaContainer(viewGroup="InfoList")
    dir.title2 = categorytitle

    feedurl = "http://api.sr.se/api/Poddradio/PoddFeed.aspx"

    if categoryid == 0:
        feedurl = "http://api.sr.se/api/Poddradio/PoddFeed.aspx"
    else:
        feedurl = "http://api.sr.se/api/Poddradio/PoddFeed.aspx?CategoryId=" + str(categoryid) 

    page = XML.ElementFromURL(feedurl)

    for item in page.getiterator('item'):

        #  Add AllProgramsMenu
        dir.Append(
            Function(
                DirectoryItem(
                    ProgramMenu,
                    item.findtext("title"),
                    subtitle=item.findtext("unit"),
                    summary=item.findtext("description"),
                    thumb=R(ICON),
                    art=R(ART)
                ),
                poddid=item.findtext("poddid")
            )
        )

    # ... and then return the container
    return dir
  
def ProgramMenu(sender, poddid):

    poddurl = "http://api.sr.se/api/rssfeed/rssfeed.aspx?Poddfeed=" + poddid

    page = XML.ElementFromURL(poddurl)

    dir = MediaContainer(viewGroup="InfoList")
    dir.title2 = page.findtext("channel/title")

    channellogo = page.findtext("channel/image/url")
    # channellogo = page.xpath("channel/itunes:image", namespaces=ITUNES_NAMESPACE).attrib.get("href")

    for item in page.getiterator('item'):

        dir.Append(
            TrackItem(
                item.findtext("link"),
                item.findtext("title"),
                subtitle=item.findtext("pubDate"),
                summary=item.findtext("description"),
                thumb=channellogo
            )
        )

    #            duration=item.find("enclosure").attrib.get("length"),

    # ... and then return the container
    return dir
