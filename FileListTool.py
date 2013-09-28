#!/usr/bin/env python

############################################################    
##                                                   Imports
############################################################    
import os
import sys
import urwid
import urwid.signals



############################################################    
##                                        DatasetEntry class
############################################################    
class DatasetEntry(urwid.WidgetWrap):
    """ Single dataset entry in the list """

    __metaclass__ = urwid.signals.MetaSignals
    signals = ['selected']

    #--------------------------------------------------------------------------
    def __init__(self, dataset, path):
        """ Constructor """

        self.dataset = dataset
        self.path    = path

        self.item = [
                    ('fixed', 15, urwid.Padding(urwid.AttrWrap(urwid.Text('%s' % str(dataset)), 'body', 'focus'), left=2)),
                    urwid.AttrWrap(urwid.Text('%s' % path), 'body', 'focus'),
                    ]

        w = urwid.Columns(self.item)
        super(DatasetEntry, self).__init__(w)

    #--------------------------------------------------------------------------
    def send_signal(self):
        """ emit signal 'selected' """
        urwid.emit_signal(self, 'selected')

    #--------------------------------------------------------------------------
    def selectable (self):
        """ Make these widgets selectable """
        return True
                                                                
    #--------------------------------------------------------------------------
    def keypress (self, size, key):
        """ Handle keypress events """

        # send signal when this sample has been selected
        if   key is 'enter':
            self.send_signal()

        # prevent options to get in focus via arrow keys
        elif key is 'right':
            pass

        else:
            return key
    

    #--------------------------------------------------------------------------
    def matchesCriteria(self, posList, negList):
        """
        Decide whether this entry is compatible with selection criteria or not
    
        Args:
            posList : tags that have to be in
            negList : tags this sample must not have
        Returns:
            bool    : return True if sample matches the selection criteria
        """

        for pos in posList:
            if pos not in self.path: return False

        for neg in negList:
            if neg in self.path: return False

        return True





############################################################    
##                                          TextOption class
############################################################    
class TextOption(urwid.WidgetWrap):
    """ Named option with textfield """

    __metaclass__ = urwid.signals.MetaSignals
    signals = ['modified']

    #--------------------------------------------------------------------------
    def __init__(self, option, key, default=''):
        """ Constructor """

        self.option  = ('option'    , u''+option+' <'+key+'>\n')
        self.default = default
        self.key     = key
        self.edit    = urwid.Edit( self.option, self.default )

        self.pile = urwid.Pile(
                        [
                            urwid.Divider(top=1),
                            self.edit
                        ] )

        super(TextOption, self).__init__( self.pile )


    #--------------------------------------------------------------------------
    def send_signal(self):
        """ emit signal 'selected' """
        urwid.emit_signal(self, 'modified')


    #--------------------------------------------------------------------------
    def selecatable(self):
        """ Make these widgets selectable """
        return True


    #--------------------------------------------------------------------------
    def keypress(self, size, key):
        """ Handle keypress events """

        # Send signal to get rid of the focus
        if key is 'enter':
            self.send_signal()

        # Anything else is done by urwid.Edit keyhandler
        else:
            self.edit.keypress(size, key)





############################################################    
##                                        FileListTool class
############################################################    
class FileListTool():
    """ The main class managing all the UI """

    #--------------------------------------------------------------------------
    def __init__(self):
        """ Constructor """

        self.palette = [
            ('body','dark cyan', '', 'standout'),
            ('focus','dark red', 'light blue', 'standout'),
            ('head','light red', 'black'),
            ('option','default,bold','','standout'),
            ('optDefault','',''),
            ]
        
        # Read available datasets and connect signals
        datasetEntries  = []
        for dataset, sample in self.getDatasetsOnGrid().iteritems():
            datasetEntry = DatasetEntry(dataset, sample)
            urwid.connect_signal( datasetEntry, 'selected', self.moveEntry, datasetEntry )
            datasetEntries.append( datasetEntry )

        # Create header and footer
        headerButtons = [ urwid.Button (   'c : create list'         ) ,
                          urwid.Button ( 'tab : change avl/sel list' ) ,
                          urwid.Button (   'f : choose filename'     ) ,
                          urwid.Button (   'p : set positive tags'   ) ,
                          urwid.Button (   'n : set negative tags'   ) ,
                          urwid.Button (   'q : Quit'                ) ]
        header = urwid.AttrMap( urwid.Columns( headerButtons    ), 'head' )
        footer = urwid.AttrMap( urwid.Text   ('selected: %d' % 0), 'head' )

        # Create Sample Widgets
        self.datasetList  = urwid.SimpleListWalker( datasetEntries )
        self.selectedList = urwid.SimpleListWalker( [] )
        self.listbox_up   = urwid.ListBox( self.datasetList  )
        self.listbox_low  = urwid.ListBox( self.selectedList )
        self.samplesPile  = urwid.Pile(
                                [
                                    urwid.LineBox( self.listbox_up  , title='Available Samples'),
                                    urwid.LineBox( self.listbox_low , title='Selected Samples' )
                                ] )

        # Create Options Widget
        self.options = urwid.SimpleListWalker(
                            [
                                TextOption('Filelist Name:', 'f', 'myList.lst'),
                                TextOption('Positive Tags:', 'p', ''          ),
                                TextOption('Negative Tags:', 'n', ''          )
                            ] )
        for option in self.options:
            urwid.connect_signal(option, 'modified', self.optionsChanged)
        self.optionsBox = urwid.LineBox ( urwid.Padding( urwid.ListBox( self.options ), left=2), title='Options')

        # Create central Columns
        self.centralColumns = urwid.Columns(
                            [
                                self.samplesPile,
                                ('fixed', 40, urwid.Padding( self.optionsBox))
                            ] )


        self.view = urwid.Frame( self.centralColumns, header=header, footer=footer )

        self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.keystroke)
        self.loop.run()


    #--------------------------------------------------------------------------
    def moveEntry(self, datasetEntry):
        """
        Move a DatasetEntry from one list to the other
    
        Args:
            datasetEntry : the DatasetEntry object selected
        Returns:
            void
        """

        # Find the list the entry appears on
        if datasetEntry in self.datasetList:
            self. datasetList.remove ( datasetEntry )
            self.selectedList.append ( datasetEntry )

        elif datasetEntry in self.selectedList:
            self. datasetList.append ( datasetEntry )
            self.selectedList.remove ( datasetEntry )
        else:
            print('Something strange happend!')
            sys.exit(1)

        self.view.set_footer( urwid.AttrMap( urwid.Text('selected: %d' % len(self.selectedList)), 'head' ) )


    #--------------------------------------------------------------------------
    def keystroke(self, key):
        """
        exists the main loop, when 'q' or 'Q' is pressed

        Args:
            key : the key pressed by the user
        Returns:
            void
        """

        # Quit via q
        if key is 'q': 
            raise urwid.ExitMainLoop()

        # create the filelist
        if key is 'c':
            createFileList()

        # Use tab to switch between datasetList and selectedList
        if key is 'tab':
            if self.samplesPile.focus_position == 0:
                self.samplesPile.set_focus( 1 )
            else:
                self.samplesPile.set_focus( 0 )

        # Handle options
        for option in self.options:
            if option.key == key:
                self.options.set_focus( self.options.index(option) )
                self.centralColumns.set_focus(1)


    #--------------------------------------------------------------------------
    def optionsChanged(self):
        """ Set focus on samples list """

        # Get selection options and filter
        for option in self.options:
            # Try to identify th eaccoring option object

        for sample in self.datasetList:
            if sample.matchesCriteria(posList=[],negList=['Zee']) == False:
                self.datasetList.remove(sample)


        self.centralColumns.set_focus(0)


    #--------------------------------------------------------------------------
    def getDatasetsOnGrid(self):
        """
        Get list of datasets on MAINZGRID
    
        Returns:
            dict : datasets stored on localgroupdisk
        """
        
        # TODO: Change this to dq2-list-datasets

        listDatasets = {147806 : 'inclusive Zee',
                        129504 : 'Diboson WW'   ,
                        113512 : 'SingleTop'    ,
                        123553 : 'DYtautau'     }
        
        return listDatasets


    #--------------------------------------------------------------------------
    def createFileList(self):
        """
        Create the file list
    
        Returns:
            void
        """

        for entry in self.selectedList:
            pass



############################################################    
##                                    Command Line Interface
############################################################    
if __name__ == '__main__':

    # Create FileListTool instance
    prg = FileListTool()


