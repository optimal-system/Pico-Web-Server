"""webserver.py 
Web server for Raspberry Pico in MicroPython

Based on library PHEW : https://github.com/pimoroni/phew
and also modules by Simon Prickett :
https://github.com/simonprickett/phewap
https://github.com/simonprickett/iss-tracker
"""
__version__ = 1.240129

import os, machine, time
import network, urequests
from phew import access_point, connect_to_wifi, is_connected_to_wifi, dns, server
from phew.template import render_template
import json
import _thread

class setup_mode:
    
    def __init__(self):
        #You can modify following constants
        self.WIFI_FILE = "wifi.json"
        self.AP_NAME   = "mypico"
        self.AP_DOMAIN = "mypico.local" 
        self.DEFAULT_LATITUDE=42.69595799733524
        self.DEFAULT_LONGITUDE=2.8787383348379447
        self.DEFAULT_PLACE="Gare de Perpignan (Center of the World, according do Dali !)"
        #Be carefull if you want to modify
        self.WIFI_MAX_ATTEMPTS = 3
        self.TEMPLATE_PATH = "templates"
        self.REBOOT=False
        
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        print("Current WLAN config :",self.wlan.ifconfig())
        networks = self.wlan.scan()        
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
        self.wifi_networks_by_strength = sorted(found_wifi_networks.items(), key = lambda x:x[1], reverse = True)
        print(self.wifi_networks_by_strength )


    def machine_reset(self):
        """Reboot the system."""
        time.sleep(1)
        print("Resetting...")
        machine.reset()

    def ap_index(self,request):
        if request.headers.get("host").lower() != self.AP_DOMAIN.lower():
            #Local domain is found, let's display front page
            return render_template(f"{self.TEMPLATE_PATH}/redirect.html", domain = self.AP_DOMAIN.lower())
        else :
            #Input data for wifi connection and other stuff if needed
            return render_template(f"{self.TEMPLATE_PATH}/index.html", \
                                   lat = str(self.DEFAULT_LATITUDE), lng = str(self.DEFAULT_LONGITUDE), \
                                   loc = self.DEFAULT_PLACE, wifis = self.wifi_networks_by_strength)

    def ap_configure(self,request):
        print("Saving wifi credentials and other data from the index.html form...")

        with open(self.WIFI_FILE, "w") as f:
            json.dump(request.form, f)
            f.close()

        print("Reboot from new thread after we have responded to the user.")
        self.REBOOT=True
        return render_template(f"{self.TEMPLATE_PATH}/configured.html", ssid = request.form["ssid"])

        
    def ap_catch_all(self,request):
        print(request.headers.get("host"),self.AP_DOMAIN,self.REBOOT)
        if self.REBOOT :
            self.machine_reset()
        if request.headers.get("host") != self.AP_DOMAIN:
            return render_template(f"{self.TEMPLATE_PATH}/redirect.html", domain = self.AP_DOMAIN)

        return "Not found.", 404

    def loop(self) :
        print("Entering Setup mode")
        server.add_route("/", handler = self.ap_index, methods = ["GET"])
        server.add_route("/configure", handler = self.ap_configure, methods = ["POST"])
        server.set_callback(self.ap_catch_all)

        ap = access_point(self.AP_NAME)
        ip = ap.ifconfig()[0]
        print("The IP address of the Access Point Web server is :",ip)
        dns.run_catchall(ip)

        server.run()

            
        
############################################

class app_mode:
    
    def __init__(self):
        #You can modify following constants
        self.WIFI_FILE = "wifi.json"
        self.AP_NAME   = "mypico"
        self.AP_DOMAIN = "mypico.local"
        self.WIFI_MAX_ATTEMPTS = 3
        self.TEMPLATE_PATH = "templates"
        #Add other variables for your app
        self.onboard_led = machine.Pin("LED", machine.Pin.OUT)
        
    def machine_reset(self):
        """Reboot the system."""
        time.sleep(1)
        print("Resetting...")
        machine.reset()

    def app_index(self,request):
        return render_template(f"{self.TEMPLATE_PATH}/appindex.html")

    def app_toggle_led(self,request):
        self.onboard_led.toggle()
        return "OK"
    
    def app_get_temperature(self,request):
        """Not particularly reliable but uses built in hardware.
        Algorithm used here is from:
        https://www.coderdojotc.org/micropython/advanced-labs/03-internal-temperature/
        """
        sensor_temp = machine.ADC(4)
        reading = sensor_temp.read_u16() * (3.3 / (65535))
        temperature = 27 - (reading - 0.706)/0.001721
        return f"{round(temperature, 1)}"
    
    def app_reset(self,request):
        # Deleting the WIFI configuration file will cause the device to reboot as
        # the access point and request new configuration.
        os.remove(self.WIFI_FILE)
        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(self.machine_reset, ())
        return render_template(f"{self.TEMPLATE_PATH}/reset.html", access_point_ssid = self.AP_NAME)

    def app_catch_all(self,request):
        return "Not found.", 404
    
    def loop(self):
        print("Entering application mode.")
        onboard_led = machine.Pin("LED", machine.Pin.OUT)
        server.add_route("/", handler = self.app_index, methods = ["GET"])
        server.add_route("/toggle", handler = self.app_toggle_led, methods = ["GET"])
        server.add_route("/temperature", handler = self.app_get_temperature, methods = ["GET"])
        server.add_route("/reset", handler = self.app_reset, methods = ["GET"])
        # Add other routes for your application...
        server.set_callback(self.app_catch_all)        
        # Start the web server...
        server.run()

        
############################################


if __name__ == '__main__': 
    print("============ webserver.py ===================") 
    print("Version :", __version__)
    s = setup_mode()
    a = app_mode()

    try:
        os.stat(a.WIFI_FILE)
        print(os.stat(a.WIFI_FILE))
        print("Wifi File was found, attempt to connect to wifi...")
        with open(a.WIFI_FILE) as f:
            wifi_current_attempt = 1
            wifi_credentials = json.load(f)
            
            while (wifi_current_attempt < a.WIFI_MAX_ATTEMPTS):
                ip_address = connect_to_wifi(wifi_credentials["ssid"], wifi_credentials["password"])

                if is_connected_to_wifi():
                    print(f"Connected to wifi, IP address {ip_address}")
                    break
                else:
                    wifi_current_attempt += 1
                    
            if is_connected_to_wifi():
                a.loop()
            else:               
                # Bad configuration, delete the credentials file, reboot
                # into setup mode to get new credentials from the user.
                print("Bad wifi connection!")
                print(wifi_credentials)
                os.remove(WIFI_FILE)
                machine_reset()

    except Exception:
        print("Either no wifi configuration file found, or something went wrong, so go into setup mode.")
        s.loop()


