import os

##################################################################################
# can this be set automatically
path = "/home/a_user/demo/app"
server_loc = "http://127.0.0.1:8000/"
##################################################################################

#############################################################################
# Functions for creating RSS feed called when podcast is created
#############################################################################

def rss_create(podcast):

    ###########################################################################################
    # used template from
    # https://resourcecenter.odee.osu.edu/digital-media-production/how-write-podcast-rss-xml
    #
    # Tag list
    # http://www.make-rss-feeds.com/rss-tags.htm
    ###########################################################################################

    # header
    rss = "<?xml version='1.0' encoding='UTF-8'?>\n"
    rss += "<rss xmlns:atom='http://www.w3.org/2005/Atom' xmlns:itunes='http://www.itunes.com/dtds/podcast-1.0.dtd' version='2.0'>\n\n"
    rss += "<channel>\n"

    # guts
    rss += "\t<link>http://" + podcast.podlink + "</link>\n"        # Add option to auto generate podcast page
    rss += "\t<language>en-us</language>\n\n"                 # ASSUMES ENGLISH FOR THE MOMENT UPDATE!!!!
    #<copyright>&#xA9;2013</copyright>
    #<webMaster>your@email.com (Your Name)</webMaster>
    #<managingEditor>your@email.com (Your Name)</managingEditor>

    rss += "\t<image>\n"
    rss += "\t\t<url>" + podcast.image_path + "</url>\n"         # Needs to be sized to 300x300 .jpg
    rss += "\t\t<title>" + podcast.podname + " logo</title>\n"
    rss += "\t\t<link>http://" + podcast.podlink + "</link>\n"
    rss += "\t</image>\n\n"

    rss += "\t<itunes:owner>\n"
    rss +=      "\t\t<itunes:name>" + podcast.it_own_name + "</itunes:name>\n"
    rss +=      "\t\t<itunes:email>" + podcast.it_own_email + "</itunes:email>\n"
    rss += "\t</itunes:owner>\n"
    rss += "\t<itunes:category text='" + podcast.it_cat + "'/>\n"  # Add category name. 
    rss +=      "\t\t <itunes:category text='" + podcast.it_subcat + "'>"   # Can be multiple sub. categories!!!! ????
    rss += "\t</itunes:category>\n"

    rss += "\t<itunes:keywords>" + podcast.it_keys + "</itunes:keywords>\n"  # Add keywords field
    rss += "\t<itunes:explicit>" + podcast.it_explicit + "</itunes:explicit>\n"
    rss += "\t<itunes:image href='" + server_loc + podcast.image_path + "' />\n"

    tmp = podcast.podname
    tmp = tmp.split(' ')
    podname = ' '.join(tmp)
    rss += "\t<atom:link href='" + server_loc + podname + ".xml' rel='self' type='application/rss+xml' />\n"
    rss += "\t<pubDate>"+ podcast.buildtime.strftime("%a, %d %b %Y %H:%M:%S %z") + " GMT" + "</pubDate>\n"   # Add time stamp for podcast creation
    rss += "\t<title>" + podcast.podname + "</title>\n"
    rss += "\t<itunes:author>" + podcast.author + "</itunes:author>\n"       # itunes author VS user?
    rss += "\t<description>" + podcast.poddesc + "</description>\n"
    rss += "\t<itunes:summary>" + podcast.it_sum + "</itunes:summary>\n"
    rss += "\t<itunes:subtitle>" + podcast.it_subtitle + "</itunes:subtitle>\n"

    rss += "\t<lastBuildDate>" + str(podcast.buildtime) + "</lastBuildDate>\n"        # Build date for the podcast ??????
  
    #######################################################################
    # Old RSS image tag
    #######################################################################

    # ender
    rss += "</channel>\n"
    rss += "</rss>"

    return rss

def rss_save(rss,user,podcast):

    #rss_path = "/var/www/html/rss/" + podcast.podname + ".xml"

    filename = podcast.podname + ".xml"
    
    # replace spaces
    filename = filename.split(" ")
    filename = "_".join(filename)

    rss_save_path = os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id), filename)
    rss_path = os.path.join('static/'+str(user.id)+'/'+str(podcast.id), filename)

    f = open(rss_save_path, 'w')
    f.write(rss)
    f.close()

    return rss_path

##################################################################################
# Functions for editing RSS feed called when an episode is added to the podcast
##################################################################################

def rss_add_ep(userpod,ep):

    rss_path = userpod.rsslink

    new_rss = "\t<item>\n"
    new_rss += "\t<title>" + ep.epname + "</title>\n"
    new_rss += "\t<description>" + ep.epdesc + "</description>\n"

    new_rss += "\t<itunes:summary>" + ep.it_sum + "</itunes:summary>\n"
    new_rss += "\t<itunes:subtitle>" + ep.it_subtitle + "</itunes:subtitle>\n"
    #new_rss += "\t<itunesu:category itunesu:code='112'>\n"    # fix Category CODE !!!! Not sure what it means (also not defined by namespace anymore)

    new_rss += "\t<enclosure url='"+server_loc +'static/'+ str(userpod.user_id) +'/'+ str(userpod.id) +'/'+ str(ep.audio_path)+"' type='audio/mpeg' length='1024'></enclosure>\n"
    new_rss += "\t<guid>http://" + userpod.podlink + "</guid>\n"                     # Unique episode page. I am going to point to the podcast page for now!!!!!

    #new_rss += "\t<itunes:duration>00:32:16</itunes:duration>\n"   # COMPUTE len HH:MM:SS
    new_rss += "\t<pubDate>" + str(userpod.buildtime) + "</pubDate>\n"
    new_rss += "\t</item>\n" 

    end_rss = "</channel>\n"
    end_rss += "</rss>"

    ################################################################################
    # Pretty Hack: Going to be hard to update previously published episodes
    ################################################################################
    rss_save_path = os.path.join(path, rss_path)
    f = open(rss_save_path, 'r')
    lines = f.readlines()
    f.close()

    print(lines)

    # delete last two lines
    lines = lines[:-2]

    f = open(rss_save_path, 'w')
    for line in lines:

        tmp = line.split('>')
        if tmp[0] == "\t<lastBuildDate":
            lastBuild = "\t<lastBuildDate>" + str(userpod.buildtime) + "</lastBuildDate>\n"  # update last build date
            f.write(lastBuild)
        else:
            f.write(line)

    f.write(new_rss)
    f.write(end_rss)
    f.close()

