import sys, os, logging
from ConfigParser import ConfigParser
from ConfigParser import NoSectionError
from socket import gethostname

class Host(object):
    log=logging.getLogger('Pipeline')

    def __init__(self, config_file=None, hostname=None):
        self.config=ConfigParser()
        if not config_file:
            root_dir=os.path.abspath(os.path.join(os.path.dirname(__file__)))
            config_file=os.path.join(root_dir, 'config', 'hosts.conf')
            
        if not os.path.exists(config_file):
            raise RuntimeError('%s does not exist' % config_file)
        self.config.read(config_file)

        if hostname and not self.config.has_section(hostname):
            raise NoSectionError(hostname)
        elif not hostname: 
            for hn in [gethostname(), gethostname().split('.')[0]]:
                if self.config.has_section(hn):
                    self.hostname=hn
                    break
            try:
                self.hostname
            except AttributeError, e:
                hn=hostname if hostname else 'localhost (%s)' % gethostname()
                raise NoSectionError(hn)
        else:
            self.hostname=hostname
        self.log.debug('host.hostname: %s' % self.hostname)

    def __str__(self):
        return self.hostname

    # trying to figure out how to wrap self.config functions, but also use
    # a decorator to give them an extra section argument...  All without
    # having to list each function by name... Want to this on getint, getfloat,
    # getboolean, items, etc.

    def get(self, key):
        return self.config.get(self.hostname, key)

    def set(self, key, value):
        return self.config.set(self.hostname, key, str(value)) # configparser only "likes" strings

    def environ(self, key=None):
        '''
        if key != None: attempt to do a lookup in the host section for any key named
          'environ.%s' % key
        if key == None: return a dict composed of all k/v pairs where k starts with 'environ.'
        '''
        if key:
            return self.config.get(self.hostname, 'environ.%s' % key)

        # return entire environ:
        environ={}
        for key in [key for key in self.config.options(self.hostname) if key.startswith('environ.')]:
            # stupid bug/feature in ConfigParser lower-cases all keys
            # work-around is to add '.upper' to key value when needed
            key2='.'.join(key.split('.')[1:])
            if key2.endswith('upper'):
                key2='.'.join(key2.split('.')[:1]).upper()

            environ[key2]=self.get(key)
        return environ
