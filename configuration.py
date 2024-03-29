#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
configuration.py - OpSys (O.Moreau)  
"""
DOCTECH = """
"""
__version__ = 1.240222

# Names of files 
CONFIGFILE  = 'config.json'
LOGFILE     = 'log.txt'
WIFI_NAME   = "CONFIGWIFI"
WIFI_DOMAIN = "configwifi.local"
CHOICES     = 'choices.csv'
OTHERDATA   = 'otherdata.csv'

# Standard modules
from machine import Pin 
import base as B

# Default values
BUTPIN    = 0
DEFAULT_LATITUDE  = '48.82927'
DEFAULT_LONGITUDE = '-3.491273'

#Text page web
WEBTITLE  = "WEB SERVER"
WEBINTRO  = "Configuration of the program"
WEBSSID   = "Select Wifi network (mandatory) :"
WEBPWD    = "Password"
WEBSSIDPH = "Your network ?"
WEBOTHER  = "OTHER CHOICE"
WEBINPUT  = "Your input ?"
WEBCHOICE = "Select an option from this list (or imput a new one) : "
WEBCHOICEPH = "Your choice ?"
WEBLAT    = "Latitude : (between -90 and 90)"
WEBLON    = "Longitude : (between -180 and 180)"
WEBSAVE   = "Saving your configuration"
WEBMAINT  = "Maintenance"
WEBTEMP   = "Internal temperature (max 50°C) : "
WEBVOLT   = "Voltage (vBus) : "
WEBLED    = "Testing internat LED"
WEBDELETE = "Erase configuration"
WEBSTOP   = "Shutdown server"

############################################"

class get_data :
    """Get your data 
    """
    
    def __init__(self):
        pass

    def get_config(self):
        return B.read_json(CONFIGFILE)

    def get_choices(self):
        choice = B.read_csv(CHOICES)
        allchoices={}
        for i in range (len(choice)):
            allchoices[choice[i][0]]=choice[i][0]
            allchoices[choice[i][0]]=(int(choice[i][1]),int(choice[i][2]))
        return allchoices
                    
    def loop(self):
        """Verification  
        """
        config=self.get_config()
        print("=====\n",CONFIGFILE)
        print(config)
        print(type(config))
        
        allchoices=self.get_choices()
        print("=====\n",CHOICES)
        print(allchoices)
        print(type(allchoices))

######################

if __name__ == '__main__': 
    #print(__doc__)
    print("============ config.py =================") 
    print("Version :", __version__)

    get   = get_data()
    get.loop()
