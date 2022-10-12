# -*- coding: UTF-8 -*
# !/usr/bin/python3
# Coded by kris van der Merwe - October 2022
# 
# USAGE:
# python3 get_fronius_inverter_data.py -d <folder to store in - end folder name with a slash>
#
# This app reads the Fronius inverter energy usages via the cloud API
# The raw data from the previous month is stored in CSV format in a folder of your choice
# Time is in Zulu time (GMT)
#

sitelist="https://api.solarweb.com/swqapi/pvsystems-list"
site    ="https://api.solarweb.com/swqapi/pvsystems"

#
#  Specify your Authentication here
#
auths={
  "AccessKeyId": "Put your fronius Solarweb KeyId here",
  "AccessKeyValue": "Put your fronius Solarweb Key value here",
  
  # This is correct, no need to change
  "Content-type": "application/json"
}

#
# Specify your target channels here - this may be specific to your solar power design
#
ch={
    'EnergyProductionTotal':'Wh', # EnergyFeedIn          + EnergySelfConsumptionTotal  
    'EnergyFeedIn':'Wh'  ,         # EnergyProductionTotal - EnergySelfConsumptionTotal 
    'EnergyPurchased':'Wh',
}

import sys
import time
from datetime import datetime
import calendar
import requests
import json
import calendar


dtm=5

def main(argv):
    datum=datetime.now()
    pyr=(datum.year if datum.month>1 else datum.year-1)
    pmt=(datum.month-1 if datum.month>1 else 12)
    fileid="%04d-%02d-%02d" % (pyr,pmt,1)    
    outputdir = ''

    #
    # If you are not using the commandline, then delete the code
    # FROM HERE, 
    if len(argv)==2 and argv[0] in ["-d", "--dir"] and argv[1][-1] in ['\\',"/"]:
        outputdir = argv[1]
    elif len(argv)>0:
        print ('\nUsage: no parameters saves in current directory, else  \npython3 get_fronius_inverter_data.py -d <save_directory ending with a slash>\n')
        sys.exit(2)
    # TO HERE       
        
    r=requests.get(sitelist, headers=auths)
    if r.status_code==200:                    
        
        nrSystems=int(r.json()['links']['totalItemsCount'])
        tnts= r.json()['pvSystemIds'] 
        
        n=len(tnts)
        while n<nrSystems:
            time.sleep( dtm )
            volg=site+"?offset="+str(len(tnts))+"&limit="+str(n+50)
            r=requests.get(volg, headers=auths)
            if r.status_code==200:
                              
                for  t in r.json()['pvSystems']:
                    if t['pvSystemId'] not in tnts:
                        tnts.append(t['pvSystemId'])
                
                n=n+50
            else:
                print(volg+" not responding. Code: "+str(r.status_code)+" !") 
                break;
       

        if nrSystems==len(tnts):
            tp=dtm*37/60
            print("Writing #"+str(len(tnts))+" inverter CSV files, each inverter taking around "+str(int(0.5+tp))+" minutes. Total around "+str(int(nrSystems*tp))+" minutes") 
            for t in tnts:
                n=0
                print(outputdir +fileid+"_"+t+".csv")            
                fw=open(outputdir +fileid+"_"+t+".csv",'w',encoding='utf-8') 
                  
                for dag in range(calendar.monthrange(pyr,pmt)[1]):
                    #
                    # Date parameters
                    #
                    logdtf="%d-%02d-%02dT00:00:00Z"%(pyr,pmt,dag+1)
                    logdtt="%d-%02d-%02dT23:59:59Z"%(pyr,pmt,dag+1)   
                   
                        
                    r=requests.get(site+"/"+t+"/histdata?from="+logdtf+"&to="+logdtt+"&channel="+','.join(ch.keys())+"&limit=288", headers=auths)
    
                    if r.status_code==200:
                        rs=r.json()
                        if n==0:
                            fw.write ('logDateTime_GMT,logDuration,'+','.join([c+'_'+ch[c] for c in ch.keys()])+',pvSystemId\n')
                            
                        for tc in rs['data']:
    
                            co= {cd['channelName']:cd['value']  for cd in tc['channels'] }
                            fw.write(tc['logDateTime']+','+str(tc['logDuration'])+','+ ','.join([( str(co[gc]) if gc in co else ' ') for gc in ch.keys()])+","+t+'\n'  )
    
    
                    else:
                        print(site+" not responding. Inverter:"+t+". Code: "+str(r.status_code)+" !") 
                        break;

                    n+=1
                    time.sleep( dtm ) 

                fw.close() 
                 

        else:
            print(site+" System number mismatch "+str(len(tnts))+" of "+ str(nrSystems)) 
    else:
        print(site+" not responding: Code "+str(r.status_code)) 
            
 
    return None,None
if __name__ == "__main__":

    main(sys.argv[1:])

    
    
