#!/usr/bin/env python

############################################################    
##                                                   Imports
############################################################    
import os
import sys
import urwid
import urwid.signals

from MainzGridManager import MainzGridManager



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
    def __str__(self):
        """ string representation """
        return self.path
    
    #--------------------------------------------------------------------------
    def __repr__(self):
        """ representation token """
        return '<DatasetEntry: '+str(self)+'>'

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
    def get_edit_text(self):
        """
        Calls the equivalent urwid.Edit widget function
    
        Returns:
            str : the text of the included Edit widget
        """

        return self.edit.get_edit_text()


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
##                                         CheckOption class
############################################################    
class CheckOption(urwid.WidgetWrap):
    """ CheckBox option """

    __metaclass__ = urwid.signals.MetaSignals
    signals = ['modified']

    #--------------------------------------------------------------------------
    def __init__(self, option, key, state=False):
        """ Constructor """

        self.option  = ('option'    , u''+option+' <'+key+'>')
        self.key     = key
        self.state   = state
        self.check   = urwid.CheckBox( u'', state=self.state )

        self.pile = urwid.Pile(
                        [
                            urwid.Divider(top=1),
                            urwid.Text(self.option),
                            self.check
                        ] )

        super(CheckOption, self).__init__( self.pile )


    #--------------------------------------------------------------------------
    def send_signal(self):
        """ emit signal 'selected' """
        urwid.emit_signal(self, 'modified')


    #--------------------------------------------------------------------------
    def keypress (self, size, key):
        """ Handle keypress events """

        return key
    

    #--------------------------------------------------------------------------
    def get_state(self):
        """
        Calls the equivalent urwid.CheckBox widget function
    
        Returns:
            bool : the state of the checkbox
        """

        return self.check.get_state()


    #--------------------------------------------------------------------------
    def toggle_state(self):
        """
        Calls the equivalent urwid.CheckBox widget function

        Returns:
            void
        """
        self.check.toggle_state()
        self.send_signal()





############################################################    
##                                        FileListTool class
############################################################    
class FileListTool():
    """ The main class managing all the UI """

    #--------------------------------------------------------------------------
    def __init__(self):
        """ Constructor """


        self.palette = [
            ('body'       , 'dark cyan'    , ''           , 'standout') ,
            ('focus'      , 'dark red'     , 'light blue' , 'standout') ,
            ('head'       , 'light red'    , ''                       ) ,
            ('option'     , 'default,bold' , ''           , 'standout') ,
            ('optDefault' , ''             , '')          ,
            ]
        
        # Read available datasets and connect signals
        self.grid      = MainzGridManager()
        datasetEntries = []
        for (dataset, sample) in self.grid.datasets:
            datasetEntry = DatasetEntry(dataset, sample)
            urwid.connect_signal( datasetEntry, 'selected', self.moveEntry, datasetEntry )
            datasetEntries.append( datasetEntry )

        # Create header and footer
        headerButtons = [ urwid.Padding( urwid.Button (   'c : create list'         ), left=1, right=1)  ,
                          urwid.Padding( urwid.Button ( '  d : toggle outpur dir'   ), left=1, right=1)  ,
                          urwid.Padding( urwid.Button ( 'tab : change avl/sel list' ), left=1, right=1)  ,
                          urwid.Padding( urwid.Button (   'f : choose filename'     ), left=1, right=1)  ,
                          urwid.Padding( urwid.Button (   'p : set positive tags'   ), left=1, right=1)  ,
                          urwid.Padding( urwid.Button (   'n : set negative tags'   ), left=1, right=1)  ,
                          urwid.Padding( urwid.Button (   'q : Quit'                ), left=1, right=1)  ]
        header = urwid.AttrMap( urwid.Columns( headerButtons    ), 'head' )
        footer = urwid.AttrMap( urwid.Text   ('selected: %d   |' % 0 ), 'head' )

        # Create Sample Widgets
        self.datasetList  = urwid.SimpleListWalker( datasetEntries )
        self.selectedList = urwid.SimpleListWalker( [] )
        self.notDisplayed = urwid.SimpleListWalker( [] )
        self.listbox_up   = urwid.ListBox( self.datasetList  )
        self.listbox_low  = urwid.ListBox( self.selectedList )
        self.samplesPile  = urwid.Pile(
                                [
                                    urwid.LineBox( self.listbox_up  , title='Available Samples'),
                                    urwid.LineBox( self.listbox_low , title='Selected Samples' )
                                ] )

        # Create Options Widget
        self.filenameOption  = TextOption  ( 'Filelist Name:'          , 'f' , 'myList.list')
        self.useDefOutputDir = CheckOption ( 'Use default output dir:' , 'd' , True        )
        self.posListOption   = TextOption  ( 'Positive Tags:'          , 'p' , ''          )
        self.negListOption   = TextOption  ( 'Negative Tags:'          , 'n' , ''          )
        self.options = urwid.SimpleListWalker( [self.filenameOption, self.useDefOutputDir, self.posListOption, self.negListOption] )
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

        # update status message
        self.setStatusMessage()


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
            return

        # create the filelist
        if key is 'c':
            self.createFileList()
            return

        # Use tab to switch between datasetList and selectedList
        if key is 'tab':
            if self.samplesPile.focus_position == 0:
                self.samplesPile.set_focus( 1 )
            else:
                self.samplesPile.set_focus( 0 )
            return

        if key is 'd':
            self.useDefOutputDir.toggle_state()
            return

        # Handle options
        for option in self.options:
            if option.key == key:
                self.options.set_focus( self.options.index(option) )
                self.centralColumns.set_focus(1)
                return


    #--------------------------------------------------------------------------
    def optionsChanged(self):
        """ Set focus on samples list """

        # Get selection options and filter
        posList = [ token.strip() for token in self.posListOption.get_edit_text().split(',') ]
        negList = [ token.strip() for token in self.negListOption.get_edit_text().split(',') ]

        # Remove empty strings from lists
        if u'' in posList: posList.remove(u'')
        if u'' in negList: negList.remove(u'')


        # Update selection list
        for sample in self.datasetList[:]:
            if sample.matchesCriteria(posList=posList, negList=negList) == False:
                self.datasetList .remove( sample )
                self.notDisplayed.append( sample )
        for sample in self.notDisplayed[:]:
            if sample.matchesCriteria(posList=posList, negList=negList) == True:
                self.datasetList .append( sample )
                self.notDisplayed.remove( sample )

        self.centralColumns.set_focus(0)


    #--------------------------------------------------------------------------
    def setStatusMessage(self, msg=''):
        """ Set update status message in footer """

        self.view.set_footer( urwid.AttrMap( urwid.Text('selected: %d   |   %s' % (len(self.selectedList), msg)), 'head' ) )


    #--------------------------------------------------------------------------
    def createFileList(self):
        """
        Create the file list
    
        Returns:
            void
        """

        self.setStatusMessage('<INFO>: creating Filelist')
        # make sure filename is not empty
        filename = self.filenameOption.get_edit_text()
        if filename == u'':
            self.setStatusMessage('<WARNING>: no filename specified!')
            return

        # make sure that at least one sample has been selected
        if len(self.selectedList) < 1:
            self.setStatusMessage('<WARNING>: no dataset selected!')
            return

        # make sure file list ends with .list
        appendedListEnding = False
        if not filename.endswith('.list'):
            filename += '.list'
            appendedListEnding = True

        # check state of default output dir checkbox
        if self.useDefOutputDir.get_state() == True:
            from ConfigUtils2  import ConfigUtils
            configParser = ConfigUtils()                                       
            configParser.setDefaultConfigName("ganga_mogon")
            listOutputPath = configParser.getSingleValueFromConfigFile("Diskpool Filelists","DefaultListOutputDir")
            filename = listOutputPath+'/'+filename

        # create sample list and call MainzGridManager
        samples = []
        for entry in self.selectedList:
            samples.append( entry.path )

        statusCode = self.grid.createFileList( filename, samples )
        if statusCode == 0:
            msg = '<INFO>: Filelist successfully created!'
            if appendedListEnding: msg += ' Added .list extension!'
            self.setStatusMessage(msg)
            return
        elif statusCode == 1:
            self.setStatusMessage('<WARNING>: error occured while creating filelist!')
            return




############################################################    
##                                    Command Line Interface
############################################################    
if __name__ == '__main__':

    # Create FileListTool instance
    prg = FileListTool()



