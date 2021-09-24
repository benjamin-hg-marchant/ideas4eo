from pyhdf.SD import SD, SDC 
from pyhdf.HDF import *
from pyhdf.VS import *

from .bits_stripping import extract

class myd06_l2:

    def __init__(self, file, name, **kwargs):
        
        sds_obj = file.select(name)
        
        self.name = name
        self.sds_info = sds_obj.info()
        self.sds_attributes = sds_obj.attributes()        
        
        if 'bit_start' in kwargs:
            data = sds_obj.get()
            self.data = extract(kwargs['bit_start'],kwargs['bit_count'],data[:,:,kwargs['bit']])
        else:
            self.data = sds_obj.get()
