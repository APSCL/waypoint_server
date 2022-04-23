import unittest
import app
import os

def run_tests():
    loader = unittest.TestLoader()
    test_dir = f"{os.path.dirname(app.__file__)}/tests"
    suite = loader.discover(test_dir)
    runner = unittest.TextTestRunner()
    runner.run(suite)
