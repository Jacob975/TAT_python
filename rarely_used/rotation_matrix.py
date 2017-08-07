#!/usr/bin/python
# Using a Least Squares Method to Determine Pose
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Import modules
import numpy as np
import math, matplotlib
from pylab import *

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Neutral Posture Coordinates (x,y,z,1)
CoRa = np.array([0,0,0,1])
# Center of Rotation (i.e. ankle)
M1, M2, M3 = np.array([0.15, 1, 0, 1]), np.array([0, 1.15, 0, 1]), np.array([-0.15, 1, 0, 1])
# markers 1, 2, & 3. The 1 at the end of each coordinate vector allows for easy 4x4 matrix muliplication. 
CoRb = np.array([0,2,0,1])
# superior Center of Rotation (i.e. knee)
Ma = np.vstack((M1,M2,M3,CoRa,CoRb))
# stacks marker and CoR coordinates into one array (can multiply all coordinates by the transformation matrix at the same time.
Mat = np.transpose(Ma)
# transposes all coordinates to allow for matrix muliplication

axis([-1.5, 1.5, -.5, 2.5])
show(scatter(Mat[0],Mat[1]))
# x, y plot of coordinates

# Known Rotation and Translation
ad = 30
# angle in degrees
ar = ad * math.pi / 180.0
# degrees to radians
t = np.array([0.1, 0.05, 0])
# translation vector
TM = np.array([[math.cos(ar), -1 * math.sin(ar), 0, t[0]], [math.sin(ar), math.cos(ar), 0, t[1]], [0,0,0,t[2]], [0,0,0,1]])
# augmented, affine transformation matrix

# Transformed Coordinates
Mbt = np.dot(TM,Mat)
Mb = np.transpose(Mbt) 

axis([-1.5, 1.5, -.5, 2.5])
show(scatter(Mbt[0],Mbt[1]))

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Least Squares Optimization to determine 3D movement from coordinate data 
# This methodology is from Soderkvisk and Wedin, 1993.
# We are assuming we just have start(Ma) and end(Mb) coordinates and need to find the rotation and translation.

# Subtract Center of Rotation from all coordinates
CoRa1 = CoRa[0:3]
# same as CoRa, just removing the 1 at the end.
Ma1 = Ma[0:3,0:3]
# neutral posture markers
Mb1 =  Mb[0:3,0:3]
# transformed markers
Ma2, Mb2 = Ma1 - CoRa1, Mb1 - CoRa1
# important to subtract the neutral posture center of rotation from all markers (they stay the same in this case since the CoR is 0,0,0)
Ma1t = np.transpose(Ma1) # transposes markers to fine means
Mb1t = np.transpose(Mb1) # transposes markers to fine means

# Covariance Matrix
ua = np.array([mean(Ma1t[0]), mean(Ma1t[1]), mean(Ma1t[2])])
# mean x, y, & z position of neutral posture markers
ub = np.array([mean(Mb1t[0]), mean(Mb1t[1]), mean(Mb1t[2])])
# mean x, y, & z position of transformed markers
Ma3, Mb3 = Ma2 - ua, Mb2 - ub
# subtract the mean marker x,y,z position from each marker
Mb4 = np.transpose(Mb3) 
C = np.dot(Mb4,Ma3)
# C is the covariance matrix

# Singular Value Decomposition
P, G, Q = np.linalg.svd(C)
# singular value decomposition	
PQ = np.dot(P,Q)
# multiplying the orthogonal vectors from SVD
d = array([(1,0,0),(0,1,0),(0,0,np.linalg.det(PQ))])
# this step and the next ensures that the obtained solution is not a reflected (see paper)
D = np.dot(P,d)

# Rotation Matrix and Translation Vector
R = np.dot(D,Q)
# This is the rotation matrix that should match the 3x3 rotation matrix embedded in matrix TM
T = np.transpose(ub) - np.dot(R,np.transpose(ua))
# This is the translation vector. 

print R
print T
