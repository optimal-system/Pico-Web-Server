# Pico-Web-Server  

webserver.py   
Web server for Raspberry Pico in MicroPython  
  
Based on library PHEW 
- https://github.com/pimoroni/phew  

and also modules by Simon Prickett :  
- https://github.com/simonprickett/phewap  
- https://github.com/simonprickett/iss-tracker   

and also Library for working with CSV files by Alec Delaney
  
There are 2 classes in this module that can be used by a main program to:  
- embark in a Raspberry Pico 
- provide first connection to set wifi  
- provide following connections to change settings (the password for example)  
- turn on and _off_ the wifi on demand (to save power)  
- set the Real Time Clock on Pico  
- read and write the config file (ssid, pwd, app data) in json  
- read data files in csv to select the config  
- keep all the text of the index.html in a data file for easy maintenance and translation  

All html files should be in a subdirectory called 'templates'. How do you do it in Github ? 
