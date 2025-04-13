# tests/test_app.py
import unittest
from server.src.app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_app_initialization(self):
        # Test basic application setup
        self.assertEqual(app.name, 'server.src.app')
        
    def test_root_route(self):
        # Test the base route if it exists
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)