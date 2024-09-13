#!/usr/bin/env python3

import asyncio
from mavsdk import System
import subprocess  
import os  
import signal  
import time  

# 杀死exe进程
def kill_process_by_name(process_name):  
    try:  
        # 使用taskkill命令结束名为process_name的进程，/F表示强制结束  
        # 注意：taskkill可能需要管理员权限来结束某些进程  
        subprocess.run(['taskkill', '/F', '/IM', process_name], check=True)  
        print(f"进程 {process_name} 已被成功结束。")  
    except subprocess.CalledProcessError as e:  
        print(f"无法结束进程 {process_name}。错误：{e}")

async def print_battery(drone):
    async for battery in drone.telemetry.battery():
        print(f"Battery: {battery.remaining_percent}")


async def print_gps_info(drone):
    async for gps_info in drone.telemetry.gps_info():
        print(f"GPS info: {gps_info}")


async def print_in_air(drone):
    async for in_air in drone.telemetry.in_air():
        print(f"In air: {in_air}")


async def print_position(drone):
    async for position in drone.telemetry.position():
        print(position)


# EXE程序的路径  
exe_path = 'C:\\Users\\Administrator\\Desktop\\MQTT-WS\\mavsdk_server_win32  -p 50051'  
system_address="udp://:14540"

async def run():
    # 使用Popen启动EXE  
    try:
        # 不管3721先结束mavsdk_server_win32再重新运行
        kill_process_by_name('mavsdk_server_win32.exe')

        # shell=True在Windows上是必需的，如果你需要运行一个.exe文件  
        # 注意：出于安全考虑，避免在不受信任的输入上使用shell=True  
        process = subprocess.Popen(exe_path, shell=True)  
    
        time.sleep(2)

        # Init the drone
        drone = System(mavsdk_server_address='localhost', port=50051)
        print("drone.connect wait...")
        await drone.connect(system_address)
        print(f"connecting: {system_address}")

        # Start the tasks
        asyncio.ensure_future(print_battery(drone))
        asyncio.ensure_future(print_gps_info(drone))
        asyncio.ensure_future(print_in_air(drone))
        asyncio.ensure_future(print_position(drone))

        while True:
            await asyncio.sleep(1)
 
    except Exception as e: 
        print(f"发生了一个错误: {e}")
    
    finally:  
        # 尝试杀死进程
        kill_process_by_name('mavsdk_server_win32.exe')
        print("end")
    
    # 脚本结束







if __name__ == "__main__":
    # Start the main function
    asyncio.run(run())



    async def get_is_armed(drone):
    async for is_armed in drone.telemetry.armed():
        data['data']['armed']=str(is_armed)
async def get_in_air(drone):
    async for in_air in drone.telemetry.in_air():
        data['data']['armed']=str(in_air)
async def get_flight_mode(drone):
    async for flight_mode in drone.telemetry.flight_mode():
        data['data']['flightMode']=flight_mode
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
        data['data']['position_state']['is_fixed']=gps_info.fix_type
        data['data']['position_state']['gps_number']=gps_info.num_satellites

async def get_eulerAngle(drone):
    async for eulerAngle in drone.telemetry.EulerAngle():
        data['data']['attitude']['roll']=eulerAngle.roll_deg
        data['data']['attitude']['pitch']=eulerAngle.pitch_deg
        data['data']['attitude']['yaw']=eulerAngle.yaw_deg