import unittest, sys, os

root=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root)

from Pipeline.Pipeline import Pipeline
from Pipeline.host import Host

class TestGraph(unittest.TestCase):
    def setUp(self):
        print 
    
    def test_graph(self):
        buffy=Host(hostname='buffy')
        p=Pipeline('test_graph', buffy, root)
        

if __name__=='__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestGraph)
    unittest.TextTestRunner(verbosity=2).run(suite)
