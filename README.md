# Pico-Web-Server  

webserver.py   
Web server for Raspberry Pico in MicroPython  
  
Based on library PHEW 
- https://github.com/pimoroni/phew  

and also modules by Simon Prickett :  
- https://github.com/simonprickett/phewap  
- https://github.com/simonprickett/iss-tracker   

and also a Library for working with CSV files by Alec Delaney.
ported from CircuitPython to MicroPython (small changes) by OM
- https://pydigger.com/pypi/circuitpython-csv
  
There are 2 classes in this module that can be used by a main program to:  
- embark in a Raspberry Pico 
- provide first connection to set wifi  
- provide following connections to change settings (the password for example)  
- turn on and _off_ the wifi on demand to save power (off is not included in Phew)  
- set the Real Time Clock on Pico  
- read and write the config file (ssid, pwd, app data) in json  
- read data files in csv to select the config  
- keep all the text of the index.html in a data file for easy maintenance and translation  


