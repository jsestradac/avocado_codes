#!/usr/bin/env python

#Recordar dejar ejecutable le archivo
#chmod +x cg.py
import sys
import rospy
import message_filters
import sensor_msgs.msg as sm
import std_msgs.msg as stdm
import tf
import pandas as pd
import roslaunch
import xml.etree.ElementTree as ET

is_abrir_play_bag = 1

if sys.argv > 2:
    print("Prueba en " + sys.argv[1] + sys.argv[2])
else:
    print("Prueba en vacio")

def save_file(obj,file_output):
    
    data = { 
        'Latitude': obj.latitude,
        'Longitude': obj.longitude,
        'Altitude': obj.altitude,
        'Roll': obj.roll,
        'Pitch': obj.pitch,
        'Yaw': obj.yaw,
        'Accx': obj.accx,
        'Accy': obj.accy,
        'Accz': obj.accz
    }
    df = pd.DataFrame(data)
    df.to_csv(file_output)

class experimentos:
    def __init__(self):

        self.latitude = []
        self.longitude = []
        self.altitude = []
        self.roll = []
        self.pitch = []
        self.yaw = []
        self.accx = []
        self.accy = []
        self.accz = []
        self.ipc = []
        self.ipc_temp = 0
        self.count = 0

        rospy.init_node('datos', anonymous=True)
        gps = message_filters.Subscriber('fix', sm.NavSatFix )
        imu = message_filters.Subscriber('vectornav/IMU', sm.Imu)
        rospy.Subscriber('IPC', stdm.Float32MultiArray,self.call_ipc)
        ts = message_filters.ApproximateTimeSynchronizer([gps, imu], 10, 0.1, allow_headerless=True)
        ts.registerCallback(self.callback)

    def callback(self,gps,imu):
        self.latitude.append(gps.latitude)
        self.longitude.append(gps.longitude)
        self.altitude.append(gps.altitude)
        #self.ipc.append(self.ipc_temp)
        quat = imu.orientation
        angles = tf.transformations.euler_from_quaternion((quat.x,quat.y,quat.z,quat.w))
        self.roll.append(angles[0])
        self.pitch.append(angles[1])
        self.yaw.append(angles[2])
        self.accx.append(imu.linear_acceleration.x)
        self.accy.append(imu.linear_acceleration.y)
        self.accz.append(imu.linear_acceleration.z)
        self.ipc.append(self.ipc_temp)
    
    def call_ipc(self,ipc):
        self.ipc_temp = ipc.data[2]*72
        
cg = experimentos()
rate = rospy.Rate(100)

if is_abrir_play_bag:
    #uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
    #roslaunch.configure_logging(uuid)
    #launch = roslaunch.parent.ROSLaunchParent(uuid, ["/home/kernighan/catkin_ws/src/carrito_golf/launch/play_bag.launch"])
    #launch.start()
    launch_file = "/home/kernighan/catkin_ws/src/carrito_golf/launch/play_bag.launch"
    tree = ET.parse(launch_file)
    root = tree.getroot()
    for arg in root.iter("arg"):
        if arg.attrib.get("name") == "file":
            arg.attrib["value"] = sys.argv[1]+sys.argv[2]+".bag"
    tree.write(launch_file)

    roslauncher = roslaunch.parent.ROSLaunchParent(rospy.get_param("/run_id"),[launch_file])
    roslauncher.start()

while (not rospy.is_shutdown()):
    cg.count += 1
    rate.sleep()
save_file(cg,sys.argv[1]+sys.argv[2]+'.csv')

if is_abrir_play_bag:
    roslauncher.shutdown()
