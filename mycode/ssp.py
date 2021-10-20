import os
from datetime import datetime, timezone
from numpy import pi, cos, sin, log, exp, arccos, tan, arctan, tanh, arctanh
import numpy as np
from mycode.position import *

class SSP:
    """A Class for handling Sound Speed Profile data"""

    def __init__(self):

        # The data attributes
        self.obs_time = None
        self.log_time = None
        self.obs_latitude = None
        self.obs_longitude = None
        self.vessel_latitude = None
        self.vessel_longitude = None
        self.obs_sample = list()
        self.obs_depth = list()
        self.obs_ss = list()
        self.proc_depth = np.array([])
        self.proc_ss = np.array([])
        self.proc_ss = np.array([])
        self.twtt_layer=np.array([])
        self.vessel_speed = None
        self.bot_depth = None

        self.metadata = dict()
        self.metadata["units"] = "rad"
        self.metadata["count"] = None
        self.metadata["geoid"] = None
        self.metadata["ellipsoid"] = None
        self.metadata["chart_datum"] = None
        self.metadata["time_basis"] = "UTC"
        self.metadata["name"] = None

    # The I/O methods:
    
    def read_mvp_file(self, fullpath):

        # Check to see whether data already exists in the object
        
        if self.obs_depth:
            raise RuntimeError('SSP object already contains a profile')

        # Check the File's existence
        print(fullpath)
        
        if os.path.exists(fullpath):
            self.metadata["Source File"] = fullpath
            print('Opening sound speed profile data file:' + fullpath)
        else:  # Raise a meaningful error
            raise RuntimeError('Unable to locate the input file' + fullpath)

        # Open, read and close the file
        svp_file = open(fullpath)
        svp_content = svp_file.read()
        svp_file.close
        
        # Save the file name as meta data
        
        self.metadata["name"] = os.path.basename(fullpath)

        # Tokenize the contents
        svp_lines = svp_content.splitlines()
                
        # Create a Position object
        pos = Position()
        
        n_lines = 0
        for line in svp_lines:
            print( line)

            n_lines += 1
            
            if line == '':
                break

            # Parse the time
            if line[0:8] == "GPS Time":
                # Extract the ZDA record
                obs = line.split()

                # Extract the UTC time string
                self.obs_time = ParseNMEA0183_ZDA(obs[2])

            # Parse the position
            if line[0:12] == "GPS Position":
                # Extract the ZDA record
                obs = line.split()

                # Extract the UTC time string
                _, self.obs_latitude, self.obs_longitude,_,_,_,_,_,_,_ = ParseNMEA0183_GGA(obs[2])

            # Parse the Depth
            if line[0:13] == "Bottom Depth:":
                obs = line.split()
                self.bot_depth=float(obs[2])
        
            # Parse the Vessel Speed
            if line[0:11] == "Ship Speed:":
                obs = line.split()
                self.vessel_speed=float(obs[2])/1.852
            

    
        # Split the record types line
        rec_type = svp_lines[n_lines].split(',')
    
        # Find the index of the Dpth(m) records
        index_depth = rec_type.index('Dpth(m)')
        
        # Find the index of the Sound Speed records
        index_ss = rec_type.index('SV(m/s)')
        
        for line in svp_lines[ n_lines + 1:]:
            obs = line.split(',')
            self.obs_depth.append( float(obs[index_depth]))
            self.obs_ss.append( float(obs[index_ss]))

        # Make sure that there are no depth reversals due to heaving

        temp = sorted(zip(self.obs_depth, self.obs_ss), key=lambda x: x[0])
        self.obs_depth, self.obs_ss = map(list, zip(*temp))

        # Remove any duplicate depths with associated sound speeds
        d_p=self.obs_depth[0]
        index = 0
        unwanted = []
        for d in self.obs_depth[1:]:
            index += 1
            if d  == d_p:
                unwanted.append(index)
            d_p = d
            
        for e in sorted( unwanted, reverse = True):
            del self.obs_depth[ e]
            del self.obs_ss[ e]
        
        # Add Numpy arrays to work with the data
        self.d = np.array(self.obs_depth)
        self.c = np.array(self.obs_ss)
        
        # Extend the profiles to the surface
        
        if self.d[0] > 0:
            self.d = np.insert(self.d,0,0)
            self.c = np.insert(self.c,0,self.c[0])
   
        # Calculate the gradients
        
        self.g = (self.c[1:] - self.c[0:-1])/(self.d[1:] - self.d[0:-1])

        # Extend the profiles to full ocean depth
        
        if self.d[-1] < 12000:
            self.d = np.append(self.d,12000)
            self.c = np.append(self.c,self.c[-1]+0.017*(12000-self.d[-2]))
            self.g = np.append(self.g,0.017)
           
        # To avoid dividing by zero assign layers with gradient g = 0 a very small value
        
        self.g[self.g == 0] =  0.001
        
        # Recalculate the sound speed profile
        
        for i in range(1,len(self.g)):
            self.c[i]=self.c[i-1]+(self.d[i] - self.d[i-1])*self.g[i-1]