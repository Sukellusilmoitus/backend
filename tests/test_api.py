from unittest.case import TestCase
import json

from src.index import app

class TestApi(TestCase):
    def setup(self):
        pass
    
    def test_api_get_target_data(self):
        response = app.test_client().get('/api/data')
        data_json = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(data_json),3)
        self.assertGreaterEqual(len(data_json["features"]),2000)
    
