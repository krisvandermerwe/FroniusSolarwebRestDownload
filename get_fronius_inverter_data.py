# -*- coding: UTF-8 -*
# !/usr/bin/python3
#
# Coded by:  Kris van der Merwe - March 2022
# Apache License 2.0
#
#
# This app reads the Fronius inverter energy usages via the cloud restAPI.
# The raw cloud API data from the previous month is stored in CSV format in a folder of your choice
# Time is in Zulu time (GMT)
#
# USAGE:
# python3 get_fronius_inverter_data.py -d save_directory_ending_with_a_slash
#

site="https://api.solarweb.com/swqapi/pvsystems"

#
#  Specify your RestApi Authentication for your account here. 
#  You set this via the Fronius www.solarweb.com website 
#
auths={
  "AccessKeyId": "Put your fronius Solarweb KeyId here",
  "AccessKeyValue": "Put your fronius Solarweb Key value here",
  # This is correct, no need to change
  "Content-type": "application/json"
}

#
# Specify your target channels here - this is specific to your solar power design
#
ch={
    'EnergyProductionTotal':'Wh', # = EnergyFeedIn          + EnergySelfConsumptionTotal  
    'EnergyFeedIn':'Wh',          # = EnergyProductionTotal - EnergySelfConsumptionTotal 
    'EnergyPurchased':'Wh',
}

import sys
import time
from datetime import datetime
import calendar
import requests
import json
import calendar

datum=datetime.now()
pyr=(datum.year if datum.month>1 else datum.year-1)
pmt=(datum.month-1 if datum.month>1 else 12)
fileid="%04d-%02d-%02d" % (pyr,pmt,1)
dtm=6

def main(argv):
    outputdir = ''
    #
    # If you are not using the commandline, then delete the code
    # FROM HERE,
    if len(argv)==2 and argv[0] in ["-d", "--dir"] and argv[1][-1] in ['\\',"/"]:
        outputdir = argv[1]
    elif len(argv)>0:
        print ('\nUsage: no parameters saves in current directory, else  \npython3 get_fronius_inverter_data.py -d save_directory_ending_with_a_slash \n')
        sys.exit(2)
    # TO HERE
    
    r=requests.get(site, headers=auths)
    if r.status_code==200:                    
        tnts=[t['pvSystemId'] for t in r.json()['pvSystems']]
        print("Writing "+str(len(tnts))+" inverter CSV files, each inverter taking about "+str(int(dtm*31/60))+" minutes")      
        
        for t in tnts:
            n=0
            print(outputdir +fileid+"_"+t+".csv")            
            fw=open(outputdir +fileid+"_"+t+".csv",'w',encoding='utf-8')   
            for d in range(calendar.monthrange(pyr,pmt)[1]):
                logdtf="%d-%02d-%02dT00:00:00Z"%(pyr,pmt,d+1)
                logdtt="%d-%02d-%02dT00:00:00Z"%((pyr if calendar.monthrange(pyr,pmt)[1]>d+1 else datum.year),(pmt if calendar.monthrange(pyr,pmt)[1]>d+1 else datum.month),(d+2 if calendar.monthrange(pyr,pmt)[1]>d+1 else 1))
                 
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
                    break

                time.sleep( dtm ) 
                n+=1
                    
            fw.close() 
    else:
        print(site+" not responding: Code "+str(r.status_code)) 
    return 

if __name__ == "__main__":
    main(sys.argv[1:])

    
    

