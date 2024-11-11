import paho.mqtt.client as mqtt

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    # Since we subscribed only for a single channel, reason_code_list contains
    # a single entry
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")

def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
    # Be careful, the reason_code_list is only present in MQTTv5.
    # In MQTTv3 it will always be empty
    if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
        print("unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)")
    else:
        print(f"Broker replied with failure: {reason_code_list[0]}")
    client.disconnect()

def on_message(client, userdata, message):
    # userdata is the structure we choose to provide, here it's a list()
    userdata.append(message.payload)
    
    # 메시지 수신 시 토픽에 따라 출력
    if message.topic == "req/call":
        print(f"민주가 필요한 게 있대: {message.payload.decode()}")
    elif message.topic == "req/drink":
        print(f"민주가 목마르대: {message.payload.decode()}")
    elif message.topic == "req/sleep":
        print(f"민주가 졸리대: {message.payload.decode()}")
    else:
        print(f"민주가 배고프대: {message.payload.decode()}")

    # 메시지가 10개를 초과하면 오래된 메시지 삭제 (최신 10개 유지)
    if len(userdata) > 10:
        userdata.pop(0)

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        # we should always subscribe from on_connect callback to be sure
        # our subscribed is persisted across reconnections.
        client.subscribe("$SYS/#")

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_subscribe = on_subscribe
mqttc.on_unsubscribe = on_unsubscribe

mqttc.user_data_set([])
mqttc.connect("mqtt.eclipseprojects.io")
mqttc.loop_forever()
print(f"Received the following message: {mqttc.user_data_get()}")