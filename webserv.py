#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
webserv.py - OpSys (O.Moreau)  
"""
DOCTECH = """
"""
__version__ = 1.240222

# Standard modules
import os , uasyncio
from machine import Pin, reset
import network, urequests
# Additional modules that must be downloaded to the Pico
from phew import access_point, connect_to_wifi, is_connected_to_wifi, dns, server
from phew.template import render_template
# modules webserv
import configuration as C
import base as B


TEMPLATES   = "templates"
WIFI_MAX_ATTEMPTS = 3
IP_ADDRESS  = "0.0.0.0"

##################################

def find_wifi():
    """find stongest wifi available
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("WLAN config :",wlan.ifconfig())
    networks = wlan.scan()        
    found_wifi_networks = {}
    for n in networks:
        ssid = n[0].decode().strip('\x00')
        if len(ssid) > 0:
            rssi = n[3]
            if ssid in found_wifi_networks:
                if found_wifi_networks[ssid] < rssi:
                    found_wifi_networks[ssid] = rssi
            else:
                found_wifi_networks[ssid] = rssi
    wifi_networks = sorted(found_wifi_networks.items(), key = lambda x:x[1], reverse = True)
    #print("DEBUG find_wifi : List of Wifi networks:",wifi_networks )
    return wifi_networks 


# def connect_wifi() :
#     config = get.get_config()
#     try_wifi = 1            
#     while (try_wifi < WIFI_MAX_ATTEMPTS):
#         #print("DEBUG main : try_wifi :",try_wifi,WIFI_MAX_ATTEMPTS)
#         IP_ADDRESS = connect_to_wifi(config["ssid"], config["password"])
#         if is_connected_to_wifi():
#             print(f"Connected to wifi, IP address {IP_ADDRESS}")
#             break
#         else:
#             try_wifi += 1              

def connect_wifi() :
    config = get.get_config()
    for try_wifi in range (1,WIFI_MAX_ATTEMPTS):
        #print("DEBUG connect_wifi :",try_wifi)
        IP_ADDRESS = connect_to_wifi(config["ssid"], config["password"])
        if is_connected_to_wifi():
            print(f"Connected to wifi, IP address {IP_ADDRESS}")
            break

##################################

class first_connect():
    """First connection thru Access point to get :
        - Wifi credentials (ssid, password)
        - 2 custom variables (myinput and mychoice)
    """
    
    def __init__(self):
        self.REBOOT=False
        self.wifi_networks=[]
        self.choices = []
    
    def fcindex(self,request):
        """Web page to get user input and choice
        """
        if request.headers.get("host").lower() != C.WIFI_DOMAIN.lower():
            return render_template(f"{TEMPLATES}/redirect.html", domain = C.WIFI_DOMAIN.lower())
        else :
            return render_template(f"{TEMPLATES}/index_fc.html", WIFIS = self.wifi_networks, CHOICES = self.choices )

    def configure(self,request):
        """record config and reboot
        """
        B.write_json(C.CONFIGFILE,request.form)
        self.REBOOT=True
        return render_template(f"{TEMPLATES}/configured.html", ssid = request.form["ssid"])

    def catch_all(self,request):
        """Reboot or redirect or error 404
        """
        print("DEBUG catch_all :",request.headers.get("host"),C.WIFI_DOMAIN)
        if self.REBOOT :
            reset()
        if request.headers.get("host") != C.WIFI_DOMAIN:
            return render_template(f"{TEMPLATES}/redirect.html", domain = C.WIFI_DOMAIN)
        return "Page Not found.", 404

    def loop(self) :
        """start first connexion
        """
        self.wifi_networks = find_wifi()
        self.choices = B.read_csv(C.CHOICES)
        server.add_route("/",          handler = self.fcindex,   methods = ["GET"])
        server.add_route("/configure", handler = self.configure, methods = ["POST"])
        server.set_callback(self.catch_all)
        ap = access_point(C.WIFI_NAME)
        ip = ap.ifconfig()[0]
        print("DEBUG first_access.loop IP :",ip)
        dns.run_catchall(ip)
        server.run()


###########################################
        
class config_web:
    """modify existing config
    """
    
    def __init__(self):
        self.REBOOT   = False
        self.SHUTDOWN = False
        get = C.get_data()

        
    def index(self,request):
        myinput = self.config.get("myinput")
        lat  = self.config.get("lat", C.DEFAULT_LATITUDE)
        lng  = self.config.get("lng", C.DEFAULT_LONGITUDE)
        return render_template(f"{TEMPLATES}/index.html", WIFIS = self.wifi_networks,\
               LAT = lat, LNG = lng, CHOICES = self.choices, MYINPUT=myinput)
    
    def configure(self,request):
        """record data
        """
        os.remove(C.CONFIGFILE)
        B.write_json(C.CONFIGFILE,request.form)
        self.REBOOT = True
        uasyncio.Loop.stop()
        uasyncio.Loop.close()
        return render_template(f"{TEMPLATES}/configured.html", ssid = request.form["ssid"])    

    def toggle_led(self,request):
        B.toggle_led()
        return "OK"
    
    def get_temperature(self,request):
        return B.pico_temperature()
    
    def get_voltage(self,request):
        return B.voltage()

    def reset(self,request):
        self.REBOOT = True
        os.remove(C.CONFIGFILE)
        reset()
        print("reset")
        return render_template(f"{TEMPLATES}/reset.html", access_point_ssid = C.WIFI_NAME)

    def shutdown(self,request):
        self.SHUTDOWN = True
        asyncio.Loop.stop()
        asyncio.Loop.close()
        return render_template(f"{TEMPLATES}/shutdown.html")


    def catch_all(self,request):
        print("DEBUG catch_all :",request.headers.get("host"),IP_ADDRESS,type(request.headers.get("host")),type(IP_ADDRESS))
        #print(self.REBOOT,self.SHUTDOWN)
        if self.REBOOT :
            reset()
        if request.headers.get("host") != IP_ADDRESS:
            return render_template(f"{TEMPLATES}/redirect.html", domain = IP_ADDRESS)
        return "Page Not found.", 404
    
    def loop(self):
        print("""Start Web server
        """)
        self.wifi_networks = find_wifi()
        print("DEBUG self.wifi_networks :",self.wifi_networks)
        connect_wifi()
        self.config = B.read_json(C.CONFIGFILE)
        self.choices = B.read_csv(C.CHOICES)
        print("DEBUG WLAN config  :",self.config['ssid'],self.config['mychoice'])
        print("DEBUG choices :",self.choices)
        server.add_route("/",            handler = self.index,           methods = ["GET"])
        server.add_route("/configure",   handler = self.configure,       methods = ["POST"])
        server.add_route("/toggle",      handler = self.toggle_led,      methods = ["GET"])
        server.add_route("/temperature", handler = self.get_temperature, methods = ["GET"])
        server.add_route("/voltage",     handler = self.get_voltage,     methods = ["GET"])
        server.add_route("/reset",       handler = self.reset,           methods = ["GET"])
        server.add_route("/shutdown",    handler = self.shutdown,        methods = ["GET"])
        server.set_callback(self.catch_all)       
        server.run()
        for _ in range (3) :
            print("The program is still running...")
        
############################################"

    
if __name__ == '__main__': 
    #print(__doc__)
    print("============ webserver.py ===================") 
    print("Version :", __version__)
    fc = first_connect()
    cw = config_web()
    get = C.get_data()
    
    # Text for the Web Configuration - not very elegant but it must be defined in main !
    WEBTITLE = C.WEBTITLE ; WEBINTRO = C.WEBINTRO
    WEBSSID = C.WEBSSID; WEBPWD=C.WEBPWD; WEBSSIDPH = C.WEBSSIDPH; WEBOTHER = C.WEBOTHER ;
    WEBINPUT = C.WEBINPUT ; WEBCHOICE = C.WEBCHOICE ; WEBCHOICEPH = C.WEBCHOICEPH ;
    WEBLAT = C.WEBLAT ; WEBLON = C.WEBLON
    WEBSAVE = C.WEBSAVE ; WEBMAINT = C.WEBMAINT ; WEBTEMP = C.WEBTEMP ; WEBLED = C.WEBLED
    WEBVOLT = C.WEBVOLT; WEBDELETE = C.WEBDELETE ; WEBSTOP = C.WEBSTOP

    if C.CONFIGFILE not in os.listdir() :
        print(f"No config file : {C.CONFIGFILE}.")
        fc.loop()
    else :
        button = Pin(C.BUTPIN, Pin.IN, Pin.PULL_UP)
        if button.value() :
            print(f"Configuration button activated to modify file : {C.CONFIGFILE}.")
            cw.loop()
    print("No configuration needed or requested.. End of program")


            
