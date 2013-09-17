import unittest, sys, os, ConfigParser

root_dir=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
sys.path.insert(0, root_dir)
from Pipeline.host import Host
config_file=os.path.join(os.path.join(root_dir, 'Pipeline', 'config', 'hosts.conf'))

class TestHost(unittest.TestCase):
    

    def setUp(self):
        print

    def _test_environ(self):
        host=Host(config_file, 'clutch')
        environ=host.environ()

        self.assertEqual(environ['ld_library_path'], '/usr/local/lib') # no key provided
        self.assertEqual(host.environ('ld_library_path'), '/usr/local/lib') # key provided
        
    def _test_missing_key(self):
        host=Host(config_file, 'clutch')
        try:
            self.assertEqual(host.environ('imaginary_key'), '/usr/local/lib') # key provided
            self.fail()
        except ConfigParser.NoOptionError:
            pass

    def test_empty_environ(self):
        host=Host(config_file, 'imaginary_host')
        self.assertEqual(str(host), 'imaginary_host')
        env=host.environ()
        self.assertEqual(type(env), type({}))
        self.assertEqual(len(env), 0)

#-----------------------------------------------------------------------

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHost)
    unittest.TextTestRunner(verbosity=2).run(suite)


