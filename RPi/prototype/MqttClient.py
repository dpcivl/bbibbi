import paho.mqtt.client as mqtt

class MqttClient:
    def __init__(self):
        self.mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message

    def run(self, target):
        self.mqttc.connect(target)
        self.mqttc.loop_forever()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
        else:
            # we should always subscribe from on_connect callback to be sure
            # our subscribed is persisted across reconnections.
            client.subscribe("req/call")
            client.subscribe("req/drink")
            client.subscribe("req/eat")
            client.subscribe("req/sleep")

    def on_message(self, client, userdata, message):
        tag = message.topic.split('/')[-1]
        if tag == "call":
            print("나한테 와봐")
        elif tag == "drink":
            print("목 말라")
        elif tag == "eat":
            print("배고파")
        elif tag == "sleep":
            print("나 이제 잘 거야")