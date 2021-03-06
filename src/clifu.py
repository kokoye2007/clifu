#!/usr/bin/env python2.7

import cookielib
import urllib2
import base64
import getopt

import getpass

import sys
import os
import platform

#import http.client
#http.client.HTTPConnection.debuglevel=True

jar = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
urllib2.install_opener(opener)

class CLIFuError(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)

def clifu_open_in_browser(url):
    if platform.system() == "Linux":
        os.system("xdg-open http://www.commandlinefu.com/" + url);
        
    if platform.system() == "Darwin":
        os.system("open http://www.commandlinefu.com/" + url);

def clifu_update_auth_cookies(username,password): 
    url = "http://www.commandlinefu.com/users/signin"
    data = bytes("username=%s&password=%s&remember=on&submit=Let+me+in!" % \
                 (username,password),"utf8");
    
    req = urllib2.Request(url,data)
    response = urllib2.urlopen(req)
    
    headers = response.getheaders()
    
    for (_,value) in headers:
        if value.find("successful-signin") != -1:
            return
        
    raise CLIFuError("Login failed for %s" % username)
    
def clifu_get_print_to_console(url,entries):
    url = "http://www.commandlinefu.com/%s" % url
    
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    
    if ( response.getcode() == 200 ):
        data = bytes.decode(response.read())
        commands = data.split("\n\n")
      
        for c in range(1,entries):
            if ( len(commands) <= c ):
                break;
            print(commands[c] + "\n")
    else:
        raise CLIFuError("HTTP Error: %d" % response.status)

def clifu_using_get_url(query,format):
    return "/commands/using/%s/%s" % (query,format)

def clifu_matching_get_url(query,sort,format):
    queryb64 = bytes.decode(base64.b64encode(query.encode()))
    query = urllib2.quote(query)
    return "/commands/matching/%s/%s/%s/%s" % (query,queryb64,sort,format)
    
def clifu_tagged_get_url(query,format):
    query = urllib2.quote(query)
    return "/commands/tagged/163/%s/%s" % (query,format)

def clifu_favourites_get_url():
    return "/commands/favourites/plaintext/0"

def usage():
    print("clifu [-h] [-u command] [-n result_count] [-w] [string_to_match]")
    print("  -h:         this help menu")
    print("  -u command: search for commands using the specified comamnd")
    print("  -n count:   number of results to display")
    print("  -w:         open the query in the systems browser")

def main():
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hwfn:u:", ["help"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
      
    entries = 5
    matching = None
    using = None
    openwebbrowser = False
    favourites = False
    format = "plaintext"
    
    if len(args) > 0:
        matching = args[0]
    
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-u"):
            using = a
        elif o in ("-n"):
            entries = int(a); 
        elif o in ("-f"):
            favourites = True 
        elif o in ("-w"):
            openwebbrowser = True
            format=""
        else:
            assert False, "Unhandled option"
    
    url = None

    if favourites:
        username = input("Username: ")
        password = getpass.getpass()
        
        url = clifu_favourites_get_url()
        clifu_update_auth_cookies(username, password)
        clifu_get_print_to_console(url, entries)
    else:
        if matching != None: 
            url = clifu_matching_get_url(matching,"sort-by-votes",format) 
            
        if using != None:
            url = clifu_using_get_url(using,format)
            
        if not(url):
            usage()
            sys.exit(2)
            
        if openwebbrowser:
            clifu_open_in_browser(url)
        else:
            clifu_get_print_to_console(url, entries)

if __name__ == "__main__":
    main()
    
