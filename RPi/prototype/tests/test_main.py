import unittest

from RPi.prototype.FileManager import FileManager
class TestMain(unittest.TestCase):
    def setUp(self):
        self.manager = FileManager()

    def test_load_json(self):
        config = self.manager.loadJson("config/config.json")

        self.assertEqual("192.168.0.59", config.get("mqtt_broker_ip"))