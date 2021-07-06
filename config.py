import os

#>>> import ideas4eo.config as conf
#>>> conf.pkg_path()

def pkg_path():
    
    """
    Function that returns the path where the pkg is located
    """
        
    return os.path.dirname(__file__)