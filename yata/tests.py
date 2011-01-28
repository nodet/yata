"""
Tests for my ToDo app
"""

import unittest
        
from yata import test_views, test_models
        
def suite():        
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromModule(test_models))
    suite.addTests(unittest.TestLoader().loadTestsFromModule(test_views))
    return suite