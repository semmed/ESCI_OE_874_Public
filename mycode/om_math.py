import numpy as np
from numpy import log10

# This file implements some math that is commonly encountered in ocean mapping, but not part of libraries such as scipy or numpy

# C4.8  Adding Incoherent Sound Levels
def incoherent_sum_log10(spl):
    pass #Remove once you add code

    # C4.8.0  Determine the Number of SPLs
    ...
    
    # C4.8.1  Check to see whether  `spl` is Iterable
    if(num_levels ...):
        return ...
    
    # C4.8.2  Initialize the Incoherent Sum
    sum_incoherent = ...
    
    # C4.8.3  Iterate Through the List
    for l in spl:
        sum_incoherent += ...
        
    # C4.8.3  Map it Back to Decibels
    return 10 * ...
        
    
def Rx(a):
    return np.array([[1, 0     ,  0     ],
                     [0, cos(a), -sin(a)],
                     [0, sin(a),  cos(a)]])
def Ry(a):
    return np.array([[ cos(a), 0,  sin(a)],
                     [ 0     , 1,  0     ],
                     [-sin(a), 0,  cos(a)]])
def Rz(a):
    return np.array([[cos(a), -sin(a), 0],
                     [sin(a),  cos(a), 0],
                     [0     ,  0     , 1]])
    