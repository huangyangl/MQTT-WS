#!/usr/bin/env python3

import asyncio
from mavsdk import System
import subprocess    
import time  
from datetime import datetime
import math  
import paho.mqtt.client as mqtt 

# EXE程序的路径
exe_mavproxy_path = ".\\MAVProxy\\mavproxy --master=tcp:127.0.0.1:5762 --out=udp:127.0.0.1:14540 --out=udp:127.0.0.1:14550  --no-console"
# exe_mavproxy_path = ".\\MAVProxy\\mavproxy --master=com14 --out=udp:127.0.0.1:14540 --out=udp:127.0.0.1:14550  --no-console"
exe_mavsdk_path = '.\\mavsdk_server_win32  -p 50051'
system_address="udp://:14540"
# MQTT服务器地址
MQTT_BROKER = "47.113.112.74"
MQTT_PORT = 1883
SUB_TOPIC = "cmd"
PUB_TOPIC = "copter"
MQTT_USERNAME = "shd01"  # 用户名
MQTT_PASSWORD = "shd01"  # 密码
MQTT_CLIENT_ID = "shd01" # ID
data={
    "tid": '43d2e632-1558-4c4e-83d2-eeb51b7a377a',
    "bid": '7578f2ac-1f12-4d47-9ab6-5de146ed7b8a',
    "timestamp": -1,
    "need_reply": 0,
    "method": 'null',
    "data": {
        "armed": 'false',
        "flying": 'false',
        "flightMode": 'LOITER',
        "latitude": -1,
        "longitude": -1,
        "relativeAlt": -1,
        "absoluteAlt": -1,
        "voltage": -1,
        "position_state": {
            "is_fixed": -1,
            "gps_number": -1
        },
        "attitude": {
            "roll": -1,
            "pitch": -1,
            "yaw": -1
        }
    }
}

# 杀死exe进程
def kill_process_by_name(process_name):  
    try:  
        # 使用taskkill命令结束名为process_name的进程，/F表示强制结束  
        # 注意：taskkill可能需要管理员权限来结束某些进程  
        subprocess.run(['taskkill', '/F', '/IM', process_name], check=True)  
        print(f"进程 {process_name} 已被成功结束。")  
    except subprocess.CalledProcessError as e:  
        print(f"无法结束进程 {process_name}。错误：{e}")

# 获取数据
async def get_is_armed(drone):
    async for is_armed in drone.telemetry.armed():
        data['data']['armed']=str(is_armed)

async def get_in_air(drone):
    async for in_air in drone.telemetry.in_air():
        data['data']['armed']=str(in_air)

async def get_flight_mode(drone):
    async for flight_mode in drone.telemetry.flight_mode():
        data['data']['flightMode']=str(flight_mode)

async def get_position(drone):
    async for position in drone.telemetry.position():
        data['data']['latitude']=position.latitude_deg
        data['data']['longitude']=position.longitude_deg
        data['data']['relativeAlt']=position.relative_altitude_m
        data['data']['absoluteAlt']=position.absolute_altitude_m

async def get_battery(drone):
    async for battery in drone.telemetry.battery():
        data['data']['voltage']=battery.voltage_v

async def get_gps_info(drone):
    async for gps_info in drone.telemetry.gps_info():
        data['data']['position_state']['is_fixed']=str(gps_info.fix_type)
        data['data']['position_state']['gps_number']=str(gps_info.num_satellites)

async def get_eulerAngle(drone):
    async for eulerAngle in drone.telemetry.attitude_euler():
        data['data']['attitude']['roll']=eulerAngle.roll_deg
        data['data']['attitude']['pitch']=eulerAngle.pitch_deg
        data['data']['attitude']['yaw']=eulerAngle.yaw_deg

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

async def run():
    
    file_mavsdk = 'mavsdklog.txt'
    fk=open(file_mavsdk, 'a')
    fk.write(str(datetime.now())+'\n')
    # 初始化MQTT客户端  
    client = mqtt.Client(client_id=MQTT_CLIENT_ID) 
    try:
        # 不管3721先结束mavsdk_server_win32再重新运行
        kill_process_by_name('mavproxy.exe')
        kill_process_by_name('mavsdk_server_win32.exe')

        # shell=True在Windows上是必需的，如果你需要运行一个.exe文件  
        # 注意：出于安全考虑，避免在不受信任的输入上使用shell=True
        process = subprocess.Popen(exe_mavproxy_path, shell=True)
        process = subprocess.Popen(exe_mavsdk_path, shell=True, stdout=fk, stderr=fk)  # stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL表示不输出log
    
        time.sleep(3)

        # Init the drone
        drone = System(mavsdk_server_address='localhost', port=50051)
        print("Confirm mavsdk_server_win32.exe is runing...")
        print("drone.connect wait...")
        await drone.connect(system_address)
        print(f"connecting: {system_address}")

        asyncio.ensure_future(get_is_armed(drone))
        asyncio.ensure_future(get_in_air(drone))
        asyncio.ensure_future(get_flight_mode(drone))
        asyncio.ensure_future(get_position(drone))
        asyncio.ensure_future(get_battery(drone))
        asyncio.ensure_future(get_gps_info(drone))
        asyncio.ensure_future(get_eulerAngle(drone))

        # 绑定连接回调函数  
        client.on_connect = on_connect  
        # 绑定消息回调函数  
        client.on_message = on_message  
        # 设置用户名和密码  
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)  
        # 连接到MQTT服务器  
        client.connect(MQTT_BROKER, MQTT_PORT, 60)  
        # 开始客户端循环，以处理网络事件
        client.loop_start() 
        print('mqtt client loop_start...')

        # 业务代码主循环
        while True:
            await asyncio.sleep(1) # 更新飞机数据
            current_timestamp = datetime.now().timestamp()
            data['timestamp']=math.floor(current_timestamp*1000)
            #print(f"json: {data}")
            # 发布消息
            client.publish('copter',payload=str(data),qos=0)
            time.sleep(1)
 
    except Exception as e:
        print(f"发生了一个错误: {e}")
        fk.close()
        # 停止客户端循环
        client.loop_stop()
        # 断开与MQTT服务器的连接
        client.disconnect()
        kill_process_by_name('mavsdk_server_win32.exe')
        kill_process_by_name('mavproxy.exe')

    finally:
        # 尝试杀死进程
        fk.close()
        # 停止客户端循环
        client.loop_stop()
        # 断开与MQTT服务器的连接
        client.disconnect()
        kill_process_by_name('mavsdk_server_win32.exe')
        kill_process_by_name('mavproxy.exe')
        print("end")
    

if __name__ == "__main__":
    # Start the main function
    asyncio.run(run())