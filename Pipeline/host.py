import sys, os
from ConfigParser import ConfigParser
from ConfigParser import NoSectionError
from socket import gethostname

class Host(object):
    def __init__(self, config_file=None, hostname=None):
        self.config=ConfigParser()
        if not config_file:
            root_dir=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..', '..'))
            fn=os.path.join(root_dir, 'config', 'hosts.conf')
            print 'fn is %s' % fn
            self.config.read(fn)
        else:
            self.config.read(config_file)


        if hostname and not self.config.has_section(hostname):
            raise NoSectionError(hostname)
        else: 
            for hn in [gethostname(), gethostname().split('.')[0]]:
                if self.config.has_section(hn):
                    self.hostname=hn
                    break
            try:
                self.hostname
            except AttributeError:
                hn=hostname if hostname else 'localhost (%s)' % gethostname()
                raise NoSectionError(hn)

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
