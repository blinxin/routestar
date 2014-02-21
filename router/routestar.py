import sys
import os
import re

class DynLoad(object):
    """Dynamically loads all .py([oc]?) files in a folder
    
    TODO: Build the exception classes
    
    """
    def __init__(self, path = None):
        if path:
            self.set_path(path)
        self.dyn_modules = {'loaded':set(), 'failed':set()}
        
    def set_path(self, directory):
        """Set the folder path to look for python files"""
        #======================================
        # verify the path given is a directory
        # if it is set the private path variable
        # accordingly
        #======================================
        if os.path.isdir(directory):
            sys.path.append(directory)
            self.__path = directory
        else:
            raise Exception('Invalid Path')
    
    def __find_python_files(self, path):
        """private interator function that searchs for python files"""
        #======================================
        # find files with non-numeric names that
        # end with .py .pyc .pyo or .pyd
        #======================================
        rx_find_py = re.compile('^(\w+)\.(?:py|pyc|pyo|pyd)$')
        
        #======================================
        # check each file found in the directory
        # to see if it is python, if it is
        # return the file to the calling function
        #======================================
        for f in os.listdir(self.__path):
            f_path = os.path.join(self.__path, f)
            if os.path.isfile(f_path):
                rx_result = rx_find_py.search(f)
                if rx_result:
                    yield rx_result.group(1)
    
    def load_modules(self):
        """import modules in the directory 
        those that cannot be loaded are skipped
        
        """
        for module in self.__find_python_files(self.__path):
            # Exclude anything we've tried to import
            # Or init.
            if module == '__init__' or \
               module in self.dyn_modules['failed'] or \
               module in self.dyn_modules['loaded'] :
                continue
            else:
                #======================================
                # try to load each variable into the
                # buildin python import function
                # if it fails, just continue
                #======================================
                try:
                    globals()['%s' % module] = __import__('%s' % module)
                except Exception as e:
                    print 'Error on startup:', e
                    self.dyn_modules['failed'].add(module)
                else:
                    self.dyn_modules['loaded'].add(module)
   
class AddRoute(object):
    """
    Decorator that tracks and allows generation of new routes within
    the python file itself rather that declared upfront.
    """
    _routes = []
    def __init__(self, arg):
        """ 
        route keeper arguments
        """
        self._arg = arg
        
    def __call__(self, route_handler):
        '''
        The part that calls the internal function
        '''
        # Add the route to the internal structure
        self._routes.append((self._arg, route_handler))
        def wrapper(*args, **kwargs):
            return route_handler(*args, **kwargs)
        return wrapper
    
    @classmethod   
    def get_routes(self):
        return self._routes
    
    @classmethod   
    def get_paths(self):
        for path in [l[0] for l in self._routes]:
            yield path