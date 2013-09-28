'''
File:        MainzGridManager.py
Author:      Christoph Weinsheimer
Email:       weinshec@students.uni-mainz.de

Description: I/O class interfacing the dq2 tools for MainzGrid
'''


############################################################    
##                                                   Imports
############################################################    
import subprocess
import shlex


############################################################    
##                                          MainzGridManager
############################################################    
class MainzGridManager():
    """ I/O class interfacing the dq2 tools for MainzGrid"""

    #--------------------------------------------------------------------------
    def __init__(self):
        """ Constructor """
        pass


    #--------------------------------------------------------------------------
    def dq2SetupReady(self):
        """
        Check if the dq2 tools are ready
    
        Returns:
            bool : True if tools are ready
        """
        pass


    #--------------------------------------------------------------------------
    def execCommand(self, command):
        """
        Execute shell command and return its output

        Args:
            command        : the shell command to be executed
        Returns:
            stdout, stderr : the stdout and stderr of the invoked command
        """

        # split command into executable and arguments
        cmd = shlex.split( command )

        # Invoke command and retrieve stdout and stderr
        proc     = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
        out, err = proc.communicate()

        return out, err

        
