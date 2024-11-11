import paho.mqtt.client as mqtt

class ClientInterface():
    def __init__(self):
        mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        mqttc.on_connect = on_connect
        mqttc.on_message = on_message
        mqttc.on_subscribe = on_subscribe
        mqttc.on_unsubscribe = on_unsubscribe
        
        mqttc.connect("mqtt.eclipseprojects.io")
        mqttc.loop_forever()