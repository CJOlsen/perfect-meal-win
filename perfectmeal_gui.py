## The Perfect Meal
## Author: Christopher Olsen
## Copyright: 2013
## License: GNU GPL v3
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <http://www.gnu.org/licenses/>.


## ************************************************************************

import wx
import wx.grid
import wx.lib.scrolledpanel as scrolled
import perfectmeal as perfmeal
import meal_building
import sys # sys is only used for one try/except loop, can easily be disabled

class NutrientGridDataTable(wx.grid.PyGridTableBase):
    ## The preferred method of using wxGrids is to have a data table that
    ## handles the data and a grid instance that handles the display.  This
    ## is the data table.
    def __init__(self, view):
        super(NutrientGridDataTable, self).__init__()
        self.data = []
        self.row_titles = []
        self.view = view

    def SetParent(self, parent):
        """ Called by whoever creates the data table, implies permission to
            access the parent's data and methods as needed """
        self.parent = parent
        
    def RefreshData(self):
        self.nutritional_groupings = self.parent.GetNutrientGroups()
        for group in self.nutritional_groupings:
            self.row_titles.append(group.upper())
            self.data.append(["","",""])

            fields = perfmeal.get_fields_for_group(group)
            for field in fields:
                self.row_titles.append(field)
                self.data.append([self.parent.current_meal.get_val(group,field),
                                  self.parent.min_vals.get_val(group,field),
                                  self.parent.max_vals.get_val(group,field)])
            
    def GetNumberRows(self):
        return len(self.data)
    def GetNumberCols(self):
        return len(self.data[0])
    def IsEmptyCell(self, row, col):
        return False
    def GetTypeName(self, row, col):
        return None
    def GetRowLabel(self, row):
        return self.row_titles[row]
    def GetRowLabelSize(self):
        return max([len(x) for x in self.row_titles]) * 6
    def GetEntryHighlight(self, row):
        if self.data[row][0] is None:
            # if no meal nutrition data available for current entry
            return None
        if self.data[row][1] is None and self.data[row][2] is None:
            # if no min or max data is available color the cell grey
            return (169, 169, 169)
        a = self.data[row][0] > self.data[row][1] or self.data[row][1] is None
        b = self.data[row][0] < self.data[row][2] or self.data[row][2] is None
        if a and b:
            # if the current entry is greater than the min and less than the
            # max, color the cell green
            return (151, 252, 151)
        else:
            if self.data[row][2] is not None and \
               self.data[row][2] < self.data[row][0]:
                # if the current entry has exceeded the max allowance color it
                # red
                return (255, 0, 0)
    def GetValue(self,row,col):
        return self.data[row][col]
    def SetValue(self, row, col, value):
        pass
    

class InteractivePanel(scrolled.ScrolledPanel):
    ## Essentially everything except the menubar, menu items, etc.
    ## Has become unruly, could possibly be broken up.
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent)
        self.parent = parent
        self.current_meal = perfmeal.get_meal([])
        self.body_weight = 150

        self.ShowWarning() # show disclaimer
        
        self.BuildUI()
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.sizer.Layout()
        
        self.Show()

        
    def BuildUI(self):
        self.sizer = wx.GridBagSizer(hgap=5, vgap=5)

        self.panel = scrolled.ScrolledPanel(parent=self)
        
        self.AddListboxes()
        self.AddNutritionalGrid()
        self.BindButtonsEtc()
        
        self.SetSizer(self.sizer)
        self.sizer.Layout()
        self.panel.SetSizerAndFit(self.sizer)

    def ShowWarning(self):
        text = "Thank you for being here! \n\nWhat is contained in this program\
is absolutely NOT sound \
nutritional advice.  This program is currently in a Proof Of Concept phase \
and all nutritional daily requirement numbers are either ballpark or \
completely wrong.\n\n\
This project is currently hosted at:\nhttps://github.com/CJOlsen/perfect-meal-win\n\
(the GNU/Linux version is at .../CJOlsen/perfect-meal) \n\nI need help managing and coding this \
project!\n\nNutritional content of over 6,500 foods is from the USDA and \
packaged into the JSON format by Ashley Williams (special thanks!) See\n\
http://ashleyw.co.uk/project/food-nutrient-database\nfor more info.\n\nIf you \
are a qualified nutritionist (or programmer) and would like to \
contribute to a Free and Open Source project please visit\n\
en.wikipedia.org/wiki/GNU_Generfal_Public_License and/or\n\
http://www.gnu.org/philosophy/free-sw.html to see how contributions to this \
project will be handled."
        wx.MessageBox(text, 'Welcome to Perfect Meal', 
            wx.OK | wx.ICON_INFORMATION)

    def BindButtonsEtc(self):
        self.Bind(wx.EVT_BUTTON, self.OnUseSelected, id=1)
        self.Bind(wx.EVT_BUTTON, self.OnRemoveSelected, id=2)
        self.Bind(wx.EVT_BUTTON, self.OnAddToMeal, id=3)
        self.Bind(wx.EVT_BUTTON, self.OnGo, id=4)
        self.Bind(wx.EVT_BUTTON, self.OnCompleteMeal, id=500) #choose better id

    def MakeNutritionalGridDataTable(self):
        """ Creates the data backend for the Nutritional Grid
            Called by AddNutritionalGrid (only)"""
        self.nutr_grid_data = NutrientGridDataTable(view=self.nutritional_grid)
        self.nutr_grid_data.SetParent(self) # so it can freely access local data
        self.min_vals, self.max_vals = \
                       perfmeal.get_benchmarks()
        self.nutr_grid_data.RefreshData()
        
    def AddNutritionalGrid(self):
        """ Creates the Nutritional Grid and requests the creation of the
            corresponding data table """
        #self.nutr_grid_panel = wx.Panel(parent=self.panel)
        self.nutritional_grid = wx.grid.Grid(self)
        self.MakeNutritionalGridDataTable()
        
        self.nutritional_groupings = self.GetNutrientGroups()
        rows = self.nutr_grid_data.GetNumberRows()
        columns = self.nutr_grid_data.GetNumberCols()
        
        
        self.nutritional_grid.CreateGrid(rows, columns)
        self.nutritional_grid.SetRowLabelSize(self.nutr_grid_data.GetRowLabelSize())
        self.nutritional_grid.SetColLabelValue(0,'current')
        self.nutritional_grid.SetColLabelValue(1,'min')
        self.nutritional_grid.SetColLabelValue(2,'max')

        self.DisplayNutritionalGridValues()

        self.sizer.Add(self.nutritional_grid,
                       pos=(0,0),
                       span=(100,4))
        self.sizer.Layout() # needed for updating the grid
        
    def RemoveNutritionalGrid(self):
        """ Needed for hard resets of the grid.
            """
        self.sizer.Remove(self.nutritional_grid)
        self.nutritional_grid.Destroy()
        
    def DisplayNutritionalGridValues(self):
        """ Populates the Nutritional Grid"""
        self.nutr_grid_data.RefreshData()
        rows = self.nutr_grid_data.GetNumberRows()
        columns = self.nutr_grid_data.GetNumberCols()
        for i in range(rows):
            for j in range(columns):
                try:
                    # this throws an error on windows machines
                    self.nutritional_grid.SetCellValue(i,
                                                       j,
                                                       str(self.nutr_grid_data.GetValue(i,j)))
                except:
                    pass
        for i in range(rows):
            self.nutritional_grid.SetRowLabelValue(i,
                                                   str(self.nutr_grid_data.GetRowLabel(i)))
        self.HighlightNutritionalGrid()

    def HighlightNutritionalGrid(self):
        for row_num in range(self.nutr_grid_data.GetNumberRows()):
            highlight = self.nutr_grid_data.GetEntryHighlight(row_num)
            if highlight is not None:
                self.nutritional_grid.SetCellBackgroundColour(row_num,
                                                              0,
                                                              highlight)

    def ResetNutritionalGrid(self):
        """ Destroys old grid and creates a new one."""
        # the preferred message passing method for updating the grid line by
        # line was getting out of hand.
        self.RemoveNutritionalGrid()
        self.AddNutritionalGrid()


    def ShowBodyWeightMessage(self):
        """ Shows a message to update body weight, needed for proper Amino Acid
            profiling. """
        # how to break text=... up into 79 char lines?
        text = "The current weight that will be used to calculate the Amino \
Acid profile is %s.  Either enter a new weight and press OK or press Cancel \
to continue with the current value.\n((THIS DOESN'T CHANGE ANYTHING RIGHT \
NOW!))" % (self.body_weight)
        dialog = wx.TextEntryDialog(None, text, "Amino Acid Profile Helper", " ")
        if dialog.ShowModal() == wx.ID_OK:
            self.body_weight = int(dialog.GetValue())
        
    def AddListboxes(self):
        """ Add the 3 listboxes and their buttons, as well as the search field.
            """
        ## Three listboxes: current meal, search results and nutrient groupings
        current_meal_label = wx.StaticText(parent=self.panel,
                                           label="Current Meal")
        self.current_meal_listbox = wx.ListBox(parent=self.panel,
                                               id=-1,
                                               pos=(3,5),
                                               size=(275,375),
                                               choices=[],
                                               style=wx.LB_MULTIPLE)
        self.current_meal_delete_button = wx.Button(parent=self.panel,
                                                    id=2,
                                                    label='Remove Selected')
        self.current_meal_complete_button = wx.Button(parent=self.panel,
                                                      id=500,
                                                      label='Complete Meal (testing)')
        self.sizer.Add(current_meal_label,
                       pos=(0,5),
                       flag=wx.TOP|wx.LEFT|wx.BOTTOM|wx.ALIGN_LEFT,
                       border=5)
        self.sizer.Add(self.current_meal_listbox,
                       pos=(1,5),
                       span=(12,1),
                       flag=wx.TOP,
                       border=5)
        self.sizer.Add(self.current_meal_delete_button,
                       pos=(13,5),
                       flag=wx.ALIGN_RIGHT,
                       border=0)
        ## make a sizer so this button can be to the left of 'remove selected'
        self.sizer.Add(self.current_meal_complete_button,
                       pos=(14,5),
                       flag=wx.ALIGN_RIGHT,
                       border=0)
        

        ## search boxes
        self.search_label = wx.StaticText(parent=self.panel, label="Search Database")
        self.search_textbox = wx.TextCtrl(parent=self.panel,
                                          id=-1,
                                          size=(275, -1))
        self.search_textbox.SetValue('Start by typing a food here!')
        self.search_button = wx.Button(parent=self.panel, id=4, label="go")
        self.search_listbox = wx.ListBox(parent=self.panel,
                                         id=-1,
                                         size=(275,300),
                                         choices=[],
                                         style=wx.LB_MULTIPLE)

        self.search_addto_button = wx.Button(parent=self.panel,
                                             id=3,
                                             label="Add To Meal")
        self.sizer.Add(self.search_label,
                       pos=(0,6),
                       flag=wx.TOP|wx.LEFT|wx.BOTTOM|wx.ALIGN_LEFT,
                       border=5)
        self.sizer.Add(self.search_textbox,
                       pos=(1,6),
                       flag=wx.TOP|wx.LEFT|wx.BOTTOM|wx.ALIGN_LEFT,
                       border=5)
        self.sizer.Add(self.search_button,
                       pos=(2,6),
                       flag=wx.TOP|wx.LEFT|wx.BOTTOM|wx.ALIGN_RIGHT,
                       border=0)
        self.sizer.Add(self.search_listbox,
                       pos=(3,6),
                       span=(10,1),
                       flag=wx.TOP,
                       border=5)
        self.sizer.Add(self.search_addto_button,
                       pos=(13,6),
                       flag=wx.ALIGN_LEFT,
                       border=0)

        ## Nutrient Groupings Box
        self.nutrient_groups_label = wx.StaticText(parent=self.panel,
                                                   id=-1,
                                                   label="Nutrient Groupings")

        self.nutrient_groups_listbox = wx.ListBox(parent=self.panel,
                                                  id=-1,
                                                  size=(275,155),
                                                  choices=['elements','vitamins',
                                                           'energy', 'sugars',
                                                           'amino_acids',
                                                           'other',
                                                           'composition'],
                                                  style=wx.LB_MULTIPLE)
        # the next three lines effectively set the default nutrient groups
        # because everything else (in this layer) asks this listbox for them
        self.nutrient_groups_listbox.Select(0) # elements
        self.nutrient_groups_listbox.Select(1) # vitamins
        self.nutrient_groups_listbox.Select(4) # amino_acids
        self.nutrient_groups_select_button = wx.Button(parent=self.panel,
                                                       id=1,
                                                       label="Use Selected")

        self.sizer.Add(self.nutrient_groups_label,
                       pos=(15,5),
                       flag=wx.ALIGN_LEFT,
                       border=5)
        self.sizer.Add(self.nutrient_groups_listbox,
                       pos=(16,5),
                       span=(5,1),
                       border=5)
        self.sizer.Add(self.nutrient_groups_select_button,
                       pos=(21,5),
                       flag=wx.ALIGN_RIGHT,
                       border=0)
    def OnGo(self, event):
        # go is the search button
        text = self.search_textbox.GetValue()
        names = perfmeal.search_like(text)
        self.search_listbox.Set(names)
        
    def OnRemoveSelected(self, event):
        # remove selected items from the current meal listbox and meal object
        to_remove_indexes = self.current_meal_listbox.GetSelections()
        to_remove_raw = self.current_meal_listbox.GetStrings()
        to_remove_strings = [x.split('--')[1] for x in to_remove_raw]
        names = [to_remove_strings[i] for i in to_remove_indexes]
        for food_name in names:
            self.current_meal.subtract(food_name)
        self.current_meal_listbox.Set(self.current_meal.get_servings_and_foods())

        self.ResetNutritionalGrid()
            
    def OnAddToMeal(self, event):
        """ Adds foods from the search results box to the current meal listbox
            and current meal object
            """
        to_add_indexes = self.search_listbox.GetSelections()
        to_add_strings = self.search_listbox.GetStrings()
        names = [to_add_strings[i] for i in to_add_indexes]
        for food_name in names:
            new_food = perfmeal.get_food(food_name)
            self.current_meal.add(new_food)
        self.current_meal_listbox.Set(self.current_meal.get_servings_and_foods())

        self.ResetNutritionalGrid()
            
    def OnUseSelected(self, event):
        # nutrient groupings listbox action
        new_groupings = self.GetNutrientGroups()
        if new_groupings == self.nutritional_groupings:
            return # groupings haven't changed, do nothing
        if "amino_acids" in new_groupings and \
           "amino_acids" not in self.nutritional_groupings:
            # if Amino Acids are being added to the mix, prompt for body weight
            self.ShowBodyWeightMessage()
        self.DisplayNutritionalGridValues()
        self.ResetNutritionalGrid()
        
    def OnCurrentMealLBSelected(self, event):
        ## these are stubs for capturing listbox selection actions (future?)
        pass
    def OnSearchLBSelected(self, event):
        pass
    def OnNutrientLBSelected(self, event):
        pass

    def OnCompleteMeal(self, event):
        ## display popup

        text = 'This button attempts to round out your currently selected meal. \
It may take a while, it may fail.  Searching a database of 6,500+ foods for \
ones that will complement the current nutritional profile is time intensive.  \
If when this finishes, everything on the left is either green or grey (NOT red) \
then the search was (probably) successful.  Continue?'
        dialog = wx.MessageDialog(None,
                                  text,
                                  'Complete Meal',
                                  wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
        if dialog.ShowModal() == wx.ID_CANCEL:
            return
##        try:
##            new_meal = meal_building.greedy_finish_with_meal(self.current_meal)
##            self.current_meal = new_meal
##        except:
##            print 'OnCompleteMeal error.', sys.exc_info()[0]
        
        new_meal = meal_building.greedy_finish_with_meal(self.current_meal)
        self.current_meal = new_meal
        self.current_meal_listbox.Set(self.current_meal.get_servings_and_foods())
        self.DisplayNutritionalGridValues()
        self.ResetNutritionalGrid()
        
    def GetNutrientGroups(self):
        indexes = self.nutrient_groups_listbox.GetSelections()
        choices=['elements','vitamins','energy', 'sugars','amino_acids',
                 'other','composition']
        return [choices[i] for i in indexes]
        
##Button and listbox ID's: (these may not be current anymore)
##  Current Meal Listbox:
##  Search Listbox:
##  Search Text Field: 
##  Search Text "Go" Button: id=4
##  
##  Add To Meal Button: id=3
##  Remove Selected Button: id=2
##  Use Selected (Nutrient Groupings)Button: id=1 
##  Nutrient Value Textboxes: id=500
##
            
        
class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1250,750))
        
        # setting up the file menu
        filemenu = wx.Menu()
        #wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxwidgets
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT, "&Exit", " Terminate the program.")
        # Creating the Menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        self.SetMenuBar(menuBar)
        self.Show(True)
        # create event bindings
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        # display the notebook
        self.sizer = wx.BoxSizer()
        self.sizer.Add(InteractivePanel(self), 1, wx.EXPAND, border=15)
        self.SetSizer(self.sizer)
        self.Layout()
        self.Show()

    def OnAbout(self, e):
        """ Bound to the 'About' menu item.  Displays a dialog box with an OK
            button.

            """
        text = "Perfect Meal is an in-progress application by Christopher \
Olsen.\n\ngithub.com/cjolsen/perfect-diet\n\n\It's best to assume that \
nothing in this app is sound dietary advice, because it probably isn't.\n\n\
Hopefully in the future, with help, this program will offer sound advice."
        dialog = wx.MessageDialog(self,
                                  text,
                                  "About Payable Hours",
                                  wx.OK)
        dialog.ShowModal()
        dialog.Destroy()

    def OnExit(self, e):
        self.Close(True)

app = wx.App()
MainWindow(None, title="Perfect Meal")
app.MainLoop()

