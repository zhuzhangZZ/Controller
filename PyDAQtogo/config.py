"""
PyDAQtogo.config
====================

loads configuration files for setting the DAQ parameters.

"""

import logging
import os.path
import yaml
import xml.etree.cElementTree as ET

#from .lib.logger import get_all_caller
#from .lib.xml2dict import xmltodict


# Load the variable definition file
def find_configfile(basename):
    """
    __convenience function__
    generates the full path from a short basefile NOT TESTED
    :param basename:
    :return: full
    """
    project_root = os.path.dirname(os.path.dirname(__file__))
    config_dir = os.path.join(project_root, 'config')
    full_name = os.path.join(config_dir, basename)
    return full_name

def read_config(filename):
    with open(filename) as file:
        param_set = yaml.load(file, Loader=yaml.FullLoader)
    return param_set
    
def save_config(param,filename):
	
	with open(filename, 'w') as file:
		documents = yaml.dump(param, file)
	return documents	

def revert_changes(self):
    self.update_config(self._config)