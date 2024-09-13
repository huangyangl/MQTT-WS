import paho.mqtt.client as mqtt 
# MQTT服务器地址  
MQTT_BROKER = "47.113.112.74"  
MQTT_PORT = 1883  
SUB_TOPIC = "cmd"
PUB_TOPIC = "copter"
MQTT_USERNAME = "shd01"  # 用户名
MQTT_PASSWORD = "shd01"  # 密码
MQTT_CLIENT_ID = "shd01" # ID
# 当连接建立后调用的回调函数  
def on_connect(client, userdata, flags, rc):  
    print("Connected mqtt server:" + MQTT_BROKER + " with result code " + str(rc))
    # 订阅主题  
    # 注意：某些MQTT服务器可能要求你在连接时提供用户名和密码后才能订阅主题  
    print('subscribe topic: '+SUB_TOPIC)
    client.subscribe(SUB_TOPIC)  

# 当接收到订阅的消息时调用的回调函数  
def on_message(client, userdata, msg):  
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic") 
  
# 初始化MQTT客户端  
client = mqtt.Client(client_id=MQTT_CLIENT_ID)
# 绑定连接回调函数  
client.on_connect = on_connect  
# 绑定消息回调函数  
client.on_message = on_message  
# 设置用户名和密码  
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)  
# 连接到MQTT服务器  
client.connect(MQTT_BROKER, MQTT_PORT, 60)  
# 发布消息
client.publish('copter',payload='Hello copter',qos=0)
# 开始客户端循环，以处理网络事件
client.loop_start() 
print('mqtt client loop_start...')
try:  
    # 执行业务代码 
    print("执行业务代码...")
    import time
    time.sleep(500)
except Exception as e: 
    print(f"发生了一个错误: {e}")
finally:  # 无论是否发生异常，都会执行的代码块
    # 停止客户端循环
    client.loop_stop()
    # 断开与MQTT服务器的连接
    client.disconnect()
    print('finished...')