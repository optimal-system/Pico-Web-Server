# Pico-Web-Server  

webserver.py   
Web server for Raspberry Pico in MicroPython  
  
Based on library PHEW : https://github.com/pimoroni/phew  
and also modules by Simon Prickett :  
https://github.com/simonprickett/phewap  
https://github.com/simonprickett/iss-tracker  
  
There are 2 classes in this module that can be used by a main program to:  
- embark in a Pico without USB connection (in production)  
- provide first connection to set wifi  
- provide following connections to change settings (for example the password)  
- turn on and _off_ the wifi on demand to save power  
- set the RTC on Pico  
- read and write the config file (ssid, pwd, app data) in json  
- read data files in csv to select the config  
- keep all the text of the index.html in a data file for easy maintenance and translation  

All html files should be in a subdirectory called 'templates'. How do you do it in Github ? 
