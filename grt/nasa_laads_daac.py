from datetime import date
from os import path

import urllib.request
import os
import json
import pprint

from . import date_converter

from .. import config

##########################################################################################

def create_reperestory(media_path,product,collection,year,month,day):
    
    """
    Function that create reperestories to store downloaded files

    Positional argument:
        product -- name of the product (eg. MYD06_L2); type = string
        collection -- collection (eg. 61); type = integer 
        year -- product year (eg. 61); type = integer 
        month -- product month (eg. 61); type = integer 
        day -- product day (eg. 61); type = integer 
    """
            
    if not os.path.exists("{}/{}".format(media_path,product)):
        os.system("mkdir {}/{}".format(media_path,product))

    if not os.path.exists("{}/{}/{}".format(media_path,product,collection)):
        os.system("mkdir {}/{}/{}".format(media_path,product,collection))

    if not os.path.exists("{}/{}/{}/{}".format(media_path,product,collection,year)):
        os.system("mkdir {}/{}/{}/{}".format(media_path,product,collection,year))
    
    if not os.path.exists("{}/{}/{}/{}/{}_{}_{}".format(media_path,product,collection,year,year,month,day)):
        os.system("mkdir {}/{}/{}/{}/{}_{}_{}".format(media_path,product,collection,year,year,month,day))
        
    return None

##########################################################################################

def get_file(product,collection,year,month,day,hour,minute):

    """
    Download a single file from NASA LAADS DAAC 
    (Level-1 and Atmosphere Archive & Distribution System Distributed Active Archive Center)
    (https://ladsweb.modaps.eosdis.nasa.gov/)

    Positional argument:
        product -- name of the product (eg. MYD06_L2); type = string
        collection -- collection (eg. 61); type = integer 
        year -- product year (eg. 61); type = integer 
        month -- product month (eg. 61); type = integer 
        day -- product day (eg. 61); type = integer 
        hour -- product hour (eg. 61); type = integer 
        minute -- product minute (eg. 61); type = integer 

    Example:
        get_file("MYD021KM",61,2015,7,18,19,35)

    Requirements:
        This function depends on the get_count_of_day function. 
    """

    err_msg = []

    # Step1: Get NASA LAADS DAAC token"
    
    try:
        token = config.nasa_laads_daac_token
    except:
        err_msg.append("Token Not found")
        token = -1
    
    # Step2: Convert (month,day) to count of day"
    
    try:
        count_of_day = date_converter.get_count_of_day(year,month,day)
    except:
        err_msg.append("Unable to compute count of days")
        count_of_day = -1

    # Step3: "
    
    if token != -1:        
        opener = urllib.request.build_opener()
        opener.addheaders = [('Authorization', 'Bearer {}'.format(token))]
        urllib.request.install_opener(opener)
        
    # Step4: Get JSON file"
    
    if token != -1 and count_of_day != -1:
        try:
            ladsweb_url = 'https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/{}/{}/{:04d}/{:03d}.json'.format(collection,product,year,count_of_day)
            with urllib.request.urlopen(ladsweb_url) as url:
                data = json.loads(url.read().decode())
        except:
            data = -1
    
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(data) 
    
    # Step5: Check if date is available"
    
    file_name = -1
    if data != -1:
        try:
            for file in data:
                file_name_prefix = '{}.A{:04d}{:03d}.{:02d}{:02d}'.format(product,year,count_of_day,hour,minute)
                if file_name_prefix in file['name']:
                    file_name = file['name']      
        except:
            pass
    
    # Step6: download the file"            
    
    status = False
    if file_name != -1: 
        
        try:
            media_path = config.media_path
        except:
            err_msg.append("Media Path Not found")
            media_path = -1
        
        if media_path !=-1: 
        
            file_path = "{}/{}/{}/{}/{}_{}_{}/{}".format(media_path,product,collection,year,year,month,day,file_name)
        
            if not path.exists(file_path):
            
                create_reperestory(media_path,product,collection,year,month,day)
            
                ladsweb_url = 'https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/61/{}/{:04d}/{:03d}/{}'.format(product,year,count_of_day,file_name)
                urllib.request.urlretrieve(ladsweb_url, file_path) 
                status = True
    
    return err_msg, file_name