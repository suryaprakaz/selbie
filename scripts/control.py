#!/usr/bin/env python
from connect import invpen
from pid import PID
import rospy, time, math
from vrep_common.msg import ObjectGroupData as OGD
from std_msgs.msg import Float64
from sensor_msgs.msg import JointState as JS

class balanceControl(invpen,PID):
	def __init__(self):
		PID.__init__(self)
		invpen.__init__(self)
		self.handles()
		self.setKp(4)	#self.setKp(1.75)			#Always do PID tuning by ziegler nicols method 38.2 because it works
		self.setKi(0)	#self.setKi(0.16)
		self.setKd(0)	#self.setKd(0.048)
		self.setPoint(0)
		self.theta = 0
		self.thetaA = 0
		self.thetaG = 0
		self.velocity = 0
		self.lwVelocity = 0
		self.rwVelocity = 0
		self.yawVelocity = 0
		self.getSensorReadings()
		self.enableSubscibers()
		self.velocityPublisherJ1 = rospy.Publisher('vrep/targetVelocityJ1', Float64, queue_size=10)
		self.velocityPublisherJ2 = rospy.Publisher('vrep/targetVelocityJ2', Float64, queue_size=10)

	def fuse(self):
		
		rospy.init_node('invpenControl')
		rospy.Subscriber('vrep/accelerometer', OGD, self.callback) #Accelerometer Callback
		#rospy.Subscriber('vrep/jointStates', JS, self.callbackJS) #JointState Callback		
		rospy.Subscriber('vrep/gyroScope', OGD, self.callbackGyro) #Gyroscope Callback
		rospy.spin()
		self.stopSimulation()
			
	def callback(self,data):
		#Theta Calculation for only Accelerometers. Works Fine. Don't Delete
		temp = 180 - math.atan2( data.floatData.data[0]*1000 , data.floatData.data[2]*1000) * (180 / math.pi)
		if temp >180.0 and temp<=360.0:
			self.thetaA = temp -360
		else:
			self.thetaA = temp
	def callbackJS(self,data):
		#print data.position
		pass

	def callbackGyro(self,data):	
		
		self.thetaG = self.thetaG + (data.floatData.data[-5] * 1000 /2.57) * 0.01
		self.theta = 0.95 * (self.thetaG)+ 0.05 * self.thetaA

		#Velocity Calculation
		
		if self.theta<=45.0 and self.theta>=-45:
			self.velocity = (self.update(self.theta))
			self.lwVelocity = 0.5 * self.velocity + 0.5 * self.yawVelocity
			self.rwVelocity = 0.5 * self.velocity - 0.5 * self.yawVelocity
		else:
			self.velocity = 0
			self.lwVelocity = 0
			self.rwVelocity = 0

		self.velocityPublisherJ1.publish(self.lwVelocity)
		self.velocityPublisherJ2.publish(-self.rwVelocity)
		print self.thetaA, self.thetaG, self.theta, self.lwVelocity, self.rwVelocity
		#self.velocityPublisherJ1.publish(1.0)
		#self.velocityPublisherJ2.publish(1.0)
		#print data.floatData.data[0]*1000,data.floatData.data[1]*1000,data.floatData.data[2]*1000
		#print  temp, self.theta, self.velocity
		time.sleep(0.01)	
			
spock = balanceControl()
spock.fuse()


