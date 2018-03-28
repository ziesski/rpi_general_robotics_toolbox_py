# Copyright (c) 2018, Rensselaer Polytechnic Institute, Wason Technology LLC
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Willow Garage, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import math
import numpy as np
import warnings

def hat(k):
    """
    Returns a 3 x 3 cross product matrix for a 3 x 1 vector
    
             [  0 -k3  k2]
     khat =  [ k3   0 -k1]
             [-k2  k1   0]
    
    :type    k: numpy.array
    :param   k: 3 x 1 vector
    :rtype:  numpy.array
    :return: the 3 x 3 cross product matrix    
    """
    
    khat=np.zeros((3,3))
    khat[0,1]=-k[2]
    khat[0,2]=k[1]
    khat[1,0]=k[2]
    khat[1,2]=-k[0]
    khat[2,0]=-k[1]
    khat[2,1]=k[0]    
    return khat

# generate 3 x 3 rotation matrix for theta degrees about k
def rot(k, theta):
    """
    Generates a 3 x 3 rotation matrix from a unit 3 x 1 unit vector axis
    and an angle in radians using the Euler-Rodrigues formula
    
        R = I + sin(theta)*hat(k) + (1 - cos(theta))*hat(k)^2
        
    :type    k: numpy.array
    :param   k: 3 x 1 unit vector axis
    :type    theta: number
    :param   theta: rotation about k in radians
    :rtype:  numpy.array
    :return: the 3 x 3 rotation matrix 
        
    """
    I = np.identity(3)
    khat = hat(k)
    khat2 = khat.dot(khat)
    return I + math.sin(theta)*khat + (1.0 - math.cos(theta))*khat2

def screw_matrix(r):
    """
    Returns the matrix G representing the 6 x 6 transformation between
    screws in a rigid body, i.e.
 
      (twist)_2 = transpose(G)*(twist)_1
         (twist) = [angular velocity, linear velocity]
      (wrench)_1 = G*(wrench)_2   
         (wrench) = [torque, force]

    :type    r: numpy.array
    :param   r: the 3 x 1 displacement vector from point 1 to point 2
    :rtype:  numpy.array
    :return: the 6 x 6 screw matrix
    """
    
    G = np.identity(6)
    G[0:3,3:6] = hat(r)
    return G

def q2R(q):
    """
    Converts a quaternion into a 3 x 3 rotation matrix according to the
    Euler-Rodrigues formula.
    
    :type    q: numpy.array
    :param   q: 4 x 1 vector representation of a quaternion q = [q0;qv]
    :rtype:  numpy.array
    :return: the 3x3 rotation matrix    
    """
    
    I = np.identity(3)
    qhat = hat(q[1:4])
    qhat2 = qhat.dot(qhat)
    return I + 2*q[0]*qhat + 2*qhat2;

def R2q(R):
    """
    Converts a 3 x 3 rotation matrix into a quaternion.  Quaternion is
    returned in the form q = [q0;qv].
    
    :type    R: numpy.array
    :param   R: 3 x 3 rotation matrix
    :rtype:  numpy.array
    :return: the quaternion as a 4 x 1 vector q = [q0;qv] 
      
    """
    
    tr = np.trace(R)
    if tr > 0:
        S = 2*math.sqrt(tr + 1)
        q = np.array([[0.25*S], \
                      [(R[2,1] - R[1,2]) / S], \
                      [(R[0,2] - R[2,0]) / S], \
                      [(R[1,0] - R[0,1]) / S]])
                      
    elif (R[0,0] > R[1,1] and R[0,0] > R[2,2]):
        S = 2*math.sqrt(1 + R[0,0] - R[1,1] - R[2,2])
        q = np.array([[(R[2,1] - R[1,2]) / S], \
                      [0.25*S], \
                      [(R[0,1] + R[1,0]) / S], \
                      [(R[0,2] + R[2,0]) / S]])
    elif (R[1,1] > R[2,2]):
        S = 2*math.sqrt(1 - R[0,0] + R[1,1] - R[2,2])
        q = np.array([[(R[0,2] - R[2,0]) / S], \
                      [(R[0,1] + R[1,0]) / S], \
                      [0.25*S], \
                      [(R[1,2] + R[2,1]) / S]])
    else:
        S = 2*math.sqrt(1 - R[0,0] - R[1,1] + R[2,2])
        q = np.array([[(R[1,0] - R[0,1]) / S], \
                      [(R[0,2] + R[2,0]) / S], \
                      [(R[1,2] + R[2,1]) / S], \
                      [0.25*S]])
    return q

def quatcomplement(q):
    """
    Generates the quaternion complement

    in:  q  = [q0;qv];
    out: qc = [q0;-qv];
    
    :type     q: numpy.array
    :param    q: 4 x 1 vector representation of a quaternion q = [q0;qv]
    :rtype:   numpy.array
    :returns: the quaternion complement as a 4 x 1 vector q = [q0;-qv]
    
    """
    return np.array([q[0],-1*q[1],-1*q[2],-1*q[3]])


def quatproduct(q):
    """
    generates matrix representation of a Hamilton quaternion product
    operator
    
    in:  q = [q0;qv];
    out: Q = [q0 -qv'; qv q0*eye(3)+ cross(qv)]
    
    :type     q: numpy.array
    :param    q: 4 x 1 vector representation of a quaternion q = [q0;qv]
    :rtype:   numpy.array
    :returns: the 4 x 4 product matrix
    """
        
    I = np.identity(3)
    Q = np.zeros((4,4))
    Q[0,0] = q[0]
    Q[0,1:4] = -q[1:4]
    Q[1:4,0] = q[1:4]
    Q[1:4,1:4] = q[0]*I+hat(q[1:4])
            
    return Q

    
def quatjacobian(q):
    """
    Returns the 4 x 3 Jacobian matrix relating an angular velocity to the 
    quarternion rate of change
    
    :type     q: numpy.array
    :param    q: 4 x 1 vector representation of a quaternion q = [q0;qv]
    :rtype:   numpy.array
    :returns: the 4 x 3 Jacobian matrix
    """
    
    I = np.identity(3)
    J = np.zeros((4,3))
    J[0,:] = 0.5 * -q[1:4]
    J[1:4,:] = 0.5 * (q[0]*I - hat(q[1:4]))
        
    return J

class Robot(object):
    """
    Holds the kinematic information for a single chain robot
    
    :attribute H: A 3 x N matrix containing the direction the joints as unit vectors, one joint per column
    :attribute P: A 3 x (N + 1) matrix containing the distance vector from i to i+1, one vector per column
    :attribute joint_type: A list of N members containing the joint type. 0 for rotary, 1 for prismatic, 2 and 3 for mobile
    :attribute joint_min: A list of N members containing the joint minimums
    :attribute joint_max: A list of N members containing the joint maximum
    :attribute M: A list of N, 6 x 6 spatial inertia matrices for the links. Optional 
    
    """
    
    
    def __init__(self, H, P, joint_type, joint_min = None, joint_max = None, M = None):
        
        """
        Construct a Robot object holding the kinematic information for a single chain robot
    
        :type  H: numpy.array
        :param H: A 3 x N matrix containing the direction the joints as unit vectors, one joint per column
        :type  H: numpy. array
        :param P: A 3 x (N + 1) matrix containing the distance vector from i to i+1, one vector per column
        :type  joint_type: list or numpy.array
        :param joint_type: A list or array of N members containing the joint type. 0 for rotary, 1 for prismatic, 2 and 3 for mobile
        :type  joint_min: list or numpy.array
        :param joint_min: A list or array of N members containing the joint type minimums
        :type  joint_max: list or numpy.array
        :param joint_max: A list or array of N members containing the joint type maximums
        :type  M: list of numpy.array
        :param M: A list of N, 6 x 6 spatial inertia matrices for the links. Optional
    
        """
        
        
        for i in xrange(H.shape[1]):
            assert (np.isclose(np.linalg.norm(H[:,i]), 1))        
        
        for j in joint_type:            
            assert (j in [0,1,2,3])                
        
        assert (H.shape[0] == 3 and P.shape[0] == 3)
        assert (H.shape[1] + 1 == P.shape[1] and H.shape[1] == len(joint_type))
        
        if (joint_min is not None and joint_max is not None):
            self.joint_min=joint_min
            self.joint_max=joint_max
        else:
            self.joint_min=None
            self.joint_max=None
               
        if M is not None:
            assert (len(M) == H.shape[1])
            for m in M:
                assert (m.shape == (6,6))
        
        self.H = H
        self.P = P
        self.joint_type = joint_type
        self.M = M
    
            
class Pose(object):
    """
    Holds a pose consisting of a rotation matrix and a vector
    
    :attribute R: The 3 x 3 rotation matrix
    :attribute p: The 3 x 1 position vector    
    """
    
    
    def __init__(self, R, p):
        """
        Construct a Pose object consisting of a rotation matrix and a vector
    
        :type  R: numpy.array
        :param R: The 3 x 3 rotation matrix
        :type  p: numpy.array
        :param p: The 3 x 1 position vector
        """    
                
        assert (R.shape == (3,3))
        assert (p.shape == (3,) or p.shape ==(3,1))
        
        self.R=R
        self.p=p.reshape((3,))
        
    def __mul__(self, other):
        R = np.dot(self.R, other.R)
        p = self.p + np.dot(self.R, other.p)
        return Pose(R,p)
    
def fwdkin(robot, theta):
    """
    Computes the pose of the robot tool flange based on a Robot object
    and the joint angles.
    
    :type    robot: Robot
    :param   robot: The robot object containing kinematic information
    :type    theta: numpy.array
    :param   theta: N x 1 array of joint angles. Must have same number of joints as Robot object
    :rtype:  Pose
    :return: The Pose of the robot tool flange    
    """    
    
    if (robot.joint_min is not None and robot.joint_max is not None):
        assert np.greater_equal(theta, robot.joint_min).all(), "Specified joints out of range"
        assert np.less_equal(theta, robot.joint_max).all(), "Specified joints out of range"
    
    p = robot.P[:,[0]]
    R = np.identity(3)
    for i in xrange(0,len(robot.joint_type)):
        if (robot.joint_type[i] == 0 or robot.joint_type[i] == 2):
            R = R.dot(rot(robot.H[:,[i]],theta[i]))
        elif (robot.joint_type[i] == 1 or robot.joint_type[i] == 3):
            p = p + theta[i] * R.dot(robot.H[:,[i]])
        p = p + R.dot(robot.P[:,[i+1]])
    return Pose(R, p)

    
def robotjacobian(robot, theta):
    """
    Computes the Jacobian matrix for the robot tool flange based on a Robot object
    and the joint angles.
    
    :type     robot: Robot
    :param    robot: The robot object containing kinematic information
    :type     theta: numpy.array
    :param    theta: N x 1 array of joint angles in radians or meters as appropriate. Must have same number of joints as Robot object.
    :rtype:   numpy.array
    :returns: The 6 x N Jacobian matrix    
    """
    
    if (robot.joint_min is not None and robot.joint_max is not None):
        assert np.greater_equal(theta, robot.joint_min).all(), "Specified joints out of range"
        assert np.less_equal(theta, robot.joint_max).all(), "Specified joints out of range"
    
    
    hi = np.zeros(robot.H.shape)
    pOi = np.zeros(robot.P.shape)
    
    p = robot.P[:,[0]]
    R = np.identity(3)
    
    pOi[:,[0]] = p
    
    H = robot.H
    P = robot.P
    joint_type = robot.joint_type
    
    for i in xrange(0, len(joint_type)):
        if (joint_type[i] == 0 or joint_type[i] == 2):
            R = R.dot(rot(H[:,[i]],theta[i]))
        elif (joint_type[i] == 1 or joint_type[i] == 3):
            p = p + theta[i] * R.dot(H[:,[i]])
        p = p + R.dot(P[:,[i+1]])
        pOi[:,[i+1]] = p
        hi[:,[i]] = R.dot(H[:,[i]])
    
    pOT = pOi[:,[len(joint_type)]]
    J = np.zeros([6,len(joint_type)])
    i = 0
    j = 0
    while (i < len(joint_type)):
        if (joint_type[i] == 0):
            J[0:3,[j]] = hi[:,[i]]
            J[3:6,[j]] = hat(hi[:,[i]]).dot(pOT - pOi[:,[i]])
        elif (joint_type[i] == 1):
            J[3:6,[j]] = hi[:,[i]]
        elif (joint_type[i] == 3):
            J[3:6,[j]] = rot(hi[:,[i+2]], theta[i+2]).dot(hi[:,[i]])
            J[0:3,[j+1]] = hi[:,[i+2]]
            J[3:6,[j+1]] = hat(hi[:,[i+2]]).dot(pOT - pOi[:,[i+2]])
            J = J[:,0:-1]
            i = i + 2
            j = j + 1
        
        i = i + 1
        j = j + 1
    return J


def subproblem0(p, q, k):
    """
    Solves Paden-Kahan subproblem 0, theta subtended between p and q according to
    
        q = rot(k, theta)*p
           ** assumes k'*p = 0 and k'*q = 0
           
    Requires that p and q are perpendicular to k. Use subproblem 1 if this is not
    guaranteed.

    :type    p: numpy.array
    :param   p: 3 x 1 vector before rotation
    :type    q: numpy.array
    :param   q: 3 x 1 vector after rotation
    :type    k: numpy.array
    :param   k: 3 x 1 rotation axis unit vector
    :rtype:  number
    :return: theta angle as scalar in radians
    """
    
    eps = np.finfo(np.float64).eps    
    assert (np.dot(k,p) < eps) and (np.dot(k,q) < eps), \
           "k must be perpendicular to p and q"
    
    norm = np.linalg.norm
    
    ep = p / norm(p)
    eq = q / norm(q)
    
    theta = 2 * np.arctan2( norm(ep - eq), norm (ep + eq))
    
    if (np.dot(k,np.cross(p , q)) < 0):
        return -theta
        
    return theta

def subproblem1(p, q, k):
    """
    Solves Paden-Kahan subproblem 1, theta subtended between p and q according to
    
        q = rot(k, theta)*p
    
    :type    p: numpy.array
    :param   p: 3 x 1 vector before rotation
    :type    q: numpy.array
    :param   q: 3 x 1 vector after rotation
    :type    k: numpy.array
    :param   k: 3 x 1 rotation axis unit vector
    :rtype:  number
    :return: theta angle as scalar in radians
    """
    
    eps = np.finfo(np.float64).eps
    norm = np.linalg.norm
    
    if norm (np.subtract(p, q)) < np.sqrt(eps):
        return 0.0
    
    
    k = np.divide(k,norm(k))
    
    pp = np.subtract(p,np.dot(p, k)*k)
    qp = np.subtract(q,np.dot(q, k)*k)
    
    epp = np.divide(pp, norm(pp))    
    eqp = np.divide(qp, norm(qp))
    
    theta = subproblem0(epp, eqp, k)
    
    if (np.abs(norm(p) - norm(q)) > norm(p)*1e-2):
        warnings.warn("||p|| and ||q|| must be the same!!!")
    
    return theta


def subproblem2(p, q, k1, k2):
    """
    Solves Paden-Kahan subproblem 2, solve for two coincident, nonparallel
    axes rotation a link according to
    
        q = rot(k1, theta1) * rot(k2, theta2) * p
    
    solves by looking for the intersection between cones of
    
        rot(k1,-theta1)q = rot(k2, theta2) * p
        
    may have 0, 1, or 2 solutions
       
    
    :type    p: numpy.array
    :param   p: 3 x 1 vector before rotations
    :type    q: numpy.array
    :param   q: 3 x 1 vector after rotations
    :type    k1: numpy.array
    :param   k1: 3 x 1 rotation axis 1 unit vector
    :type    k2: numpy.array
    :param   k2: 3 x 1 rotation axis 2 unit vector
    :rtype:  list of number pairs
    :return: theta angles as list of number pairs in radians
    """
    
    eps = np.finfo(np.float64).eps
    norm = np.linalg.norm
    
    k12 = np.dot(k1, k2)
    pk = np.dot(p, k2)
    qk = np.dot(q, k1)
    
    # check if solution exists
    if (np.abs( 1 - k12**2) < eps):
        warnings.warn("No solution - k1 != k2")
        return []
    
    a = (np.array([[k12, -1], [-1, k12]]).dot(np.array([pk, qk]))) / (k12**2 - 1)
    
    bb = (np.dot(p,p) - np.dot(a,a) - 2*a[0]*a[1]*k12)
    if (np.abs(bb) < eps): bb=0
    
    if (bb < 0):
        warnings.warn("No solution - no intersection found between cones")
        return []
    
    gamma = np.sqrt(bb) / norm(np.cross(k1,k2))
    if (np.abs(gamma) < eps):
        cm=np.array([k1, k2, np.cross(k1,k2)]).transpose()
        c1 = np.dot(cm, np.hstack((a, gamma)))
        theta2 = subproblem1(k2, p, c1)
        theta1 = -subproblem1(k1, q, c1)
        return [(theta1, theta2)]
    
    cm=np.array([k1, k2, np.cross(k1,k2)]).transpose()
    c1 = np.dot(cm, np.hstack((a, gamma)))
    c2 = np.dot(cm, np.hstack((a, -gamma)))
    theta1_1 = -subproblem1(q, c1, k1)
    theta1_2 = -subproblem1(q, c2, k1)
    theta2_1 =  subproblem1(p, c1, k2)
    theta2_2 =  subproblem1(p, c2, k2)
    return [(theta1_1, theta2_1), (theta1_2, theta2_2)]

def subproblem3(p, q, k, d):
    
    """
    Solves Paden-Kahan subproblem 3,solve for theta in
    an elbow joint according to
    
        || q + rot(k, theta)*p || = d
        
    may have 0, 1, or 2 solutions
    
    :type    p: numpy.array
    :param   p: 3 x 1 position vector of point p
    :type    q: numpy.array
    :param   q: 3 x 1 position vector of point q
    :type    k: numpy.array
    :param   k: 3 x 1 rotation axis for point p
    :type    d: number
    :param   d: desired distance between p and q after rotation
    :rtype:  list of numbers
    :return: list of valid theta angles in radians        
    
    """
    
    norm=np.linalg.norm
    
    pp = np.subtract(p,np.dot(np.dot(p, k),k))
    qp = np.subtract(q,np.dot(np.dot(q, k),k))
    dpsq = d**2 - ((np.dot(k, np.add(p,q)))**2)
    
    bb=-(np.dot(pp,pp) + np.dot(qp,qp) - dpsq)/(2*norm(pp)*norm(qp))
    
    if dpsq < 0 or np.abs(bb) > 1:
        warnings.warn("No solution - no rotation can achieve specified distance")
        return []
    
    theta = subproblem1(pp/norm(pp), qp/norm(qp), k)
    
    phi = np.arccos(bb)
    if np.abs(phi) > 0:
        return [theta + phi, theta - phi]
    else:
        return [theta]
    
    