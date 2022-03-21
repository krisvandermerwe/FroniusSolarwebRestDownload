# FroniusSolarwebRestDownload
Download monthly data from every Fronius inverter connected to your Fronius Website account.
The app will find all the inverters assigned to your account.

This is a simple batch process you can run after monthend (to be safe run a day after monthend to cope with timezone differences).
So this app reads the raw Fronius inverter energy usages via the cloud RestAPI and saves the previous month's data in CSV files in a folder of your choice.

You need to open the "get_fronius_inverter_data.py" source file to edit your security tokens generated via the solarweb.com account.

Add further data "channels" if you have batteries connected to your solar system.
The headers in the CSV file will contain the channels you have specified.

Note times are in Zulu time zone (GMT). This is the safest because it seems the Cloud API and inverters may have different zones.
So add or subtract the necessay time difference for your zone, after you have imported the CSV files.

The fronius inverter IDs are in the CSV files to ensure accurate processing 

 USAGE:
 python3 get_fronius_inverter_data.py -d save_directory_ending_with_a_slash  
 
 Linux and Windoze use different slashes for folders
 If you do not specify the -d parameter, it saves in the current directory
 
 There is a time delay between each - required by Fronius
  
 
