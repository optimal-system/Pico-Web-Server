#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
base.py - OpSys (O.Moreau)
"""
__version__ = 1.240222

import time, json
from machine import Pin, ADC
import csv
# module de configuration pour HOROLAJ
import configuration as C

LOGFILE = C.LOGFILE
CSV1 = C.CHOICES
CSV2 = C.OTHERDATA

print(LOGFILE)


######### MATH ###########

def Map(value, fromLow, fromHigh, toLow, toHigh):
    return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow

########### DATA ##############

def Log(*args) :
    entry = str(args)
    for i in ("""()'",""") :
        entry = entry.replace(i," ")
    logtime = time.localtime()
    file = LOGFILE
    with open(file, 'a',encoding="utf-8") as f:
        f.write(str(logtime) + "->" + entry + "\n")
    print (entry)    

def read_json(file):
    """Lecture d'un fichier JSON"""
    with open(file) as f:
        dico = json.load(f)
    #print("DEBUG read_json :",dico,type(dico))
    return dico

def write_json(file,dico):
    """Ecriture d'un fichier JSON"""
    with open(file, "w") as f:
        json.dump(dico, f)
    #print("DEBUG write_json :",dico,type(dico))
    return True

def read_csv(file):
    data=[]
    with open(file) as f:
        csv_reader = csv.reader(f, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                #print(f'DEBUG : read_csv : Données importées : {", ".join(row)}')
                pass
            else :
                try :
                    if   file == CSV1  : tup=(row[0]),int(row[1]),int(row[2])
                    elif file == CSV2  : tup=int(row[0]),int(row[1]),int(row[2]),int(row[3]),int(row[4]),int(row[5])
                    else : Log("ERREUR : no model to follow!")
                    data.append(tup)
                except :
                    Log("Wrong data : ",line_count,row)
            line_count += 1
        if line_count <= 1 : Log("ERROR : No data")
        data.sort()
        #print("DEBUG read_csv :",data,type(data))
        return data

def convert(s):
    """To be use with international characters
    Remplacement des codes 'bytes' par des caractères UTF8
    Attention : Fonction à compléter selon usage"""
    cs=s.replace ('Ã ','à')
    cs=cs.replace('Ã¢','â')
    cs=cs.replace('Ã©','é')
    cs=cs.replace('Ã«','ë')
    cs=cs.replace('Ã¨','è')
    cs=cs.replace('Ãª','ê')
    cs=cs.replace('Ã®','î')
    cs=cs.replace('Ã¯','ï')
    cs=cs.replace('Ã´','ô')
    cs=cs.replace('Ã¹','ù')
    cs=cs.replace('Ã§','ç')
    return cs


####### HARDWARE #########
def toggle_led():
    Pin("LED", Pin.OUT).toggle()
    return "OK"

def voltage() :
    """Use the ADC channel connected to pin v3.3 out, Pin 29.
    """
    vsysChannel = ADC(29)
    adcReading  = vsysChannel.read_u16()
    adcVoltage  = (adcReading * 3.3) / 65535
    vsysVoltage = adcVoltage * 3
    vbusVoltage = vsysVoltage + 0.275 # At 100mA
    #print ("Voltages vBUS: {0}, vSYS: {1}, vADC: {2} ".format(vbusVoltage,vsysVoltage,adcVoltage))
    return f"{round(vbusVoltage, 1)}"
    
def pico_temperature():
    sensor_temp = ADC(4)
    reading = sensor_temp.read_u16() * (3.3 / (65535))
    temperature = 27 - (reading - 0.706)/0.001721
    return f"{round(temperature, 1)}"
