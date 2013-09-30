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
import os.path


############################################################    
##                                          MainzGridManager
############################################################    
class MainzGridManager():
    """ I/O class interfacing the dq2 tools for MainzGrid"""

    __SITENAME__    = 'MAINZGRID_LOCALGROUPDISK'
    __LISTCOMMAND__ = 'dq2-list-dataset-site2'
    __REQFILES__    = 'dq2-list-files -r'
    __PATH_PREFIX__ = '/project/atlas/atlaslocalgroupdisk/'

    #--------------------------------------------------------------------------
    def __init__(self):
        """ Constructor """

        # Get dictionary of datasets on localgroupdisk
        self.datasets = self.readDatasets()
        

    #--------------------------------------------------------------------------
    def readDatasets(self):
        """
        Invoke a DQ2 list command to gather all available samples on the grid site
    
        Returns:
            list : list of pairs (datasetID , datasetName)
        """

        samples = []

        # Invoke list command
        out, err = self.execCommand( self.__LISTCOMMAND__ + ' ' + self.__SITENAME__ )

        # Iterate over lines and gather information
        for line in out.splitlines():
            if line == '\n': continue

            # Get dataset ID
            dsId = -1
            for token in ['mc11','mc12','data11','data12']:
                if token in line:
                    try:
                        dsIdPosition = line.find('.',line.find(token))+1
                        dsId =   int( line[ dsIdPosition: line.find('.', dsIdPosition) ] )
                    except:
                        pass

            # Add sample to dictionary
            samples.append( (dsId,line) )

        return samples


    #--------------------------------------------------------------------------
    def createFileList(self, filename, samples):
        """
        request files for each sample and write them into a list file
    
        Args:
            filename : path of the filelist
            samples  : list of requested samples
        Returns:
            int      : status 0 - ok; status 1 - failure
        """

        # Create file
        f = open(filename, 'w')

        # Iterate over requested samples
        for sample in samples:

            # get list of files
            out, err = self.execCommand(self.__REQFILES__+' '+sample)

            # iterate of lines and add absolute path prefix
            for line in out.splitlines():
                
                # Filter for non-root files
                if '.root' not in line: continue

                # Create full path
                fullPath = os.path.join    ( self.__PATH_PREFIX__ , line )
                fileSize = (os.path.getsize ( fullPath                    ) >> 20) / 1024.0  # size in GB
                f.write( fullPath + '\t%.3f\n' % fileSize )

        # Close the output file
        f.close()

        return 0


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

        
