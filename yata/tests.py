"""
Tests for my ToDo app
"""

import unittest
        
from yata import test_views, test_models, test_xml
        
def suite():        
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromModule(test_models))
    suite.addTests(unittest.TestLoader().loadTestsFromModule(test_views))
    suite.addTests(unittest.TestLoader().loadTestsFromModule(test_xml))
    return suite