#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python

# importing libraries
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import csv
import time
import rospy
import math
import roslib; roslib.load_manifest(PKG)
import rospy
import tf

# ROS messages.
#subscribe to
from nav_msgs.msg import Odometry
#publish to
from cloud_msgs.msg import convert_msg


#node that subscribes to the localization, calculates first order velocity from [x,z]
#coordinates at 2 time steps, changes [x,z] to [x,y] and changes quaternion to euler angles for heading

#from localization receive[x,z,t (sec), t (nsec), quaternion(4X1)]
#publishes to PlotMap and Path Follower
t1=None,t2=None,x1=None,x2=None,z1=None,z2=None
#calculate velocity
def velocity(t3,x3,z3):
    global t1,t2,x1,x2,z1,z2
    if t1==None:
        t1 = t3,z1=z3,x1=x3
        return 0
    elif t2==None:
        t1 = t2,z1=z2,x1=x2
        t2 = t3,z2=z3,x2=x3
        return 0
    else:
        #second order approximation (all other time steps)
        vx_SO=(x3-2*x2+x1)/(t3-2*t2+t1)
        vz_SO=(x3-2*x2+x1)/(t3-2*t2+t1)
        velocity=m.sqrt(vz_SO**2+vx_SO**2)
        #reinitialize t,x,z for next call of function
        t1=t2,z1=z2,x1=x2,t2=t3,z2=z3,x2=x3
        return velocity

class QuatToEuler():
    def __init__(self):

        # Create subscribers and publishers.
        sub_odom  = rospy.Subscriber("localization", Odometry, self.odom_callback)
        self.pub_localization = rospy.Publisher("conversion", convert_msg)

        rospy.spin()

    # Odometry callback function.
    def odom_callback(self, msg):
        # Convert quaternions to Euler angles.
        (roll, pitch, yaw) = tf.transformations.euler_from_quaternion([msg.pose.pose.orientation.x, msg.pose.pose.orientation.y, msg.pose.pose.orientation.z, msg.pose.pose.orientation.w])
        
        t3 = msg.header.stamp.secs + msg.header.stamp.nsecs * 1e-9
        x3 = msg.pose.pose.position.x
        z3 = msg.pose.pose.position.z
        
        self.convert_msg.x = x3
        self.convert_msg.y = z3
        self.convert_msg.v = velocity(t3, x3, z3)
        self.convert_msg.heading=0
        
        print("roll:", roll, "pitch:", pitch, "yaw:", yaw)
#         self.convert_msg.roll = roll
#         self.convert_msg.pitch = pitch
#         self.convert_msg.yaw  = yaw
        
        

# Main function.    
if __name__ == '__main__':
    # Initialize the node and name it.
    rospy.init_node('conversion')
    # Go to class functions that do all the heavy lifting. Do error checking.
    try:
        quat_to_euler = QuatToEuler()
    except rospy.ROSInterruptException:
        pass
