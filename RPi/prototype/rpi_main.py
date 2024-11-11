import sys
sys.path.append('/home/hyoin/000.Projects/bbibbi')

from RPi.prototype.FileManager import FileManager
from RPi.prototype.MqttClient import MqttClient

class Main:
    def __init__(self):
        self.flie_manager = FileManager()
        self.client = MqttClient()
    
    def run(self):
        config = self.flie_manager.loadJson("config/config.json")
        broker_ip = config.get("mqtt_broker_ip")
        # broker_ip 가지고 mqtt 커넥트
        self.client.run(broker_ip)

    def release(self):
        # 종료 시 불러올 메서드
        pass

if __name__ == "__main__":
    Main().run()