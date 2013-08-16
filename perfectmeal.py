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

####Levels of The Program (this file):
####	Class Structure (data types)
####		Food(object)
####		Meal(Food)
####	
####	Data and Benchmarks (data moved to nutrient_subgroups.py)
####		daily_min, daily_max 
####		various data for the program
####	
####	JSON Considerations
####		Food_Group_Filter
####		Name_Filter
####		open JSON file
####		read in JSON objects (filtered and not)
####		
####	Making Food objects and lists of Food objects
####		(isolates the algorithms from JSON considerations)
####
####	Searching Algorithms (moved to meal_building.py)
####		brute force (to-do)
####		Greedy algorithms
####			based on Comparators (balance returns a "valid" result)
####
####    GUI Specific Methods (interface for perfectmeal_gui.py)
####            get_fields()
####

debugging = False

import copy
import string
import json
import os # to find current directory (to find the json database)
import sys # same, in case the os method fails

#############################################################################
##################### class structure (data types) ##########################
#############################################################################

class Food(object):
    def __init__(self, nutritional_groupings, json_obj=None, name=None):
        """ The Food object has standard attributes for:
            -name: name of the food, optional
            -nutritional_groupings: a subset of ['elements', 'vitamins', 'energy', 'sugars',
                                     'amino_acids', 'other', 'composition']
                       used to choose which dictionaries to initialize
            -the seven dictionaries listed in the nutritional_groupings list
            
            If a json_obj is included the dictionaries will be populated with
            the data (as filtered by the nutritional_groupings list)
            """
        ## For comparisons to work the nutritional_groupings list will need to be the
        ## same for all Foods being used (one *could* add try/excepts to
        ## the "add" method of the Meal class to "fix" this)
        self.name = name
        assert type(nutritional_groupings) is list
        self.nutritional_groupings = nutritional_groupings     
        for i in self.nutritional_groupings:
            assert i in ['elements', 'vitamins', 'energy', 'sugars',
                         'amino_acids', 'other', 'composition']
        if 'elements' in self.nutritional_groupings:
            self.elements = {'Sodium, Na': None, 'Phosphorus, P': None,
                              'Manganese, Mn': None, 'Iron, Fe': None,
                              'Potassium, K': None, 'Fluoride, F': None,
                              'Selenium, Se': None, 'Magnesium, Mg': None,
                              'Zinc, Zn': None, 'Copper, Cu': None,
                              'Calcium, Ca': None}
        if 'vitamins' in self.nutritional_groupings:
            self.vitamins = {'Niacin': None, 'Menaquinone-4': None, 'Thiamin': None,
                             'Folate, food': None, 'Vitamin B-6': None,
                             'Tocopherol, gamma': None, 'Carotene, beta': None,
                             'Pantothenic acid': None, 'Vitamin E, added': None,
                             'Tocopherol, beta': None,
                             'Vitamin C, total ascorbic acid': None,
                             'Tocopherol, delta': None, 'Cryptoxanthin, beta': None,
                             'Vitamin D3 (cholecalciferol)': None, 'Lycopene': None,
                             'Vitamin B-12, added': None, 'Vitamin A, IU': None,
                             'Retinol': None, 'Vitamin A, RAE': None,
                             'Dihydrophylloquinone': None,
                             'Vitamin E (alpha-tocopherol)': None,
                             'Lutein + zeaxanthin': None, 'Betaine': None,
                             'Riboflavin': None, 'Vitamin D': None,
                             'Vitamin D2 (ergocalciferol)': None,
                             'Carotene, alpha': None, 'Folic acid': None,
                             'Folate, total': None, 'Vitamin B-12': None,
                             'Choline, total': None,
                             'Vitamin K (phylloquinone)': None,
                             'Vitamin D (D2 + D3)': None, 'Folate, DFE': None}
        if 'energy' in self.nutritional_groupings:
            self.energy = {'Energy': None}
        if 'sugars' in self.nutritional_groupings:
            self.sugars = {'Galactose': None, 'Starch': None, 'Lactose': None,
                           'Sucrose': None, 'Maltose': None, 'Fructose': None,
                           'Glucose (dextrose)': None}
        if 'amino_acids' in self.nutritional_groupings:
            self.amino_acids = {'Lysine': None, 'Alanine': None,
                                'Glycine': None, 'Proline': None, 'Serine': None,
                                'Arginine': None, 'Glutamic acid': None,
                                'Phenylalanine': None, 'Leucine': None,
                                'Methionine': None, 'Histidine': None,
                                'Valine': None, 'Tryptophan': None,
                                'Isoleucine': None, 'Threonine': None,
                                'Aspartic acid': None, 'Cystine': None,
                                'Tyrosine': None}
        if 'other' in self.nutritional_groupings:
            self.other = {'Alcohol, ethyl': None, 'Stigmasterol': None,
                          'Fatty acids, total trans-monoenoic': None,
                          'Theobromine': None, 'Caffeine': None,
                          'Fatty acids, total trans': None,
                          'Fatty acids, total monounsaturated': None,
                          'Beta-sitosterol': None,
                          'Fatty acids, total saturated': None,
                          'Fatty acids, total trans-polyenoic': None,
                          'Campesterol': None, 'Cholesterol': None, 'Ash': None,
                          'Fatty acids, total polyunsaturated': None,
                          'Phytosterols': None}
        if 'composition' in self.nutritional_groupings:
            self.composition = {'Fiber, total dietary': None,
                                'Adjusted Protein': None, 'Water': None,
                                'Total lipid (fat)': None, 'Protein': None,
                                'Carbohydrate, by difference': None,
                                'Sugars, total': None}
        if json_obj is not None:
            self.populate_from_json(json_obj)
    def _portion_helper(self, json_object):
        """ Takes a json_object, writes the smallest serving size (in grams)
            and unit of measurement to memory.
            Returns nothing.
            """
        portions = sorted(json_object['portions'], key=lambda k: k['grams'])
        if len(portions) == 0:
            self.unit = "100g"
            self.serving_size = 100
        else:
            smallest = portions[0]
            self.unit = smallest['unit']
            self.serving_size = smallest['grams']
    def populate_from_json(self, json_object):
        ## **** THIS IS AT LIKE 40% FUNCTIONALITY ****
        ##
        ## ALL VALUES COMING IN FROM JSON ARE PER 100g SO THEY MUST BE SCALED
        ## TO THE SERVING SIZE *AFTER* BEING CONVERTED TO MG!!!
        """ This takes a json_object and populates the active groups from it
            """
        assert type(json_object) is dict
        self.name = json_object['description']
        self._portion_helper(json_object)
        serv_size_conv_fact = self.serving_size/100. # json data is per 100g
        converter = {'g':1000., 'mg': 1., 'mcg': (1/1000.)} # normalize to mg
        serving_size = json_object['portions']
        #print 'serving_size, self.serving_size', serving_size, self.serving_size
        
        for nutr_group in self.nutritional_groupings:
            for nutrient in json_object['nutrients']:
                if nutrient['group'] == nutr_group.capitalize() and\
                   nutrient['units'] in ['g','mg', 'mcg']:
                    new_value = nutrient['value'] * converter[nutrient['units']]* \
                                serv_size_conv_fact
                    self.__dict__[nutr_group][nutrient['description']] = new_value
                else:
                    if nutr_group == "amino_acids" and\
                       nutrient['units'] in ['g','mg', 'mcg']:
                        new_value = nutrient['value'] * \
                                    converter[nutrient['units']]* \
                                    serv_size_conv_fact
                        self.__dict__["amino_acids"][nutrient['description']] = new_value
                
        ## may need a lookup table for IU to mg conversion for different
        ## vitamins and elements
        ## measurements not in g, mg or mcg are being ignored!!!
                    
    def d(self, string):
        ## d is for dictionary
        ## this gets the __dict__'s out of the algorithm layer
        return self.__dict__[string]
    def display(self):
        print ''
        print 'Food Name:'
        print self.name
        print ''
        print 'Nutritional Groupings: '
        print self.nutritional_groupings
        print ''
    def display_value(self, name):
        for group in self.nutritional_groupings:
            for item_name in self.__dict__[group]:
                if item_name == name:
                    print "Name:", name, " Value: ", self.__dict__[group][name]
    def get_val(self, group, item):
        ## hacky way to deal with the 'null' meal
        try:
            return self.__dict__[group][item]
        except:
            return None
    def get_name(self):
        return self.name
    def set_name(self, name):
        assert type(name) is str
        self.name = name
    def get_element(name):
        return self.elements[name]
    def get_vitamin(name):
        return self.vitamins[name]
    def get_energy(name):
        return self.energy[name]
    def get_sugar(name):
        return self.sugars[name]
    def get_amino_acid(name):
        return self.amino_acids[name]
    def get_other(name):
        return self.others[name]
    def get_composition(name):
        return self.composition[name]
       
class Meal(Food):
    ## identical to the Food superclass with the addition of combination
    ## and comparison methods, and a self.foods attribute to keep a list of
    ## foods contained in the meal
    ## self.foods is optional since benchmark meals (daily min and max, etc)
    ## are also of this class
    def __init__(self, nutritional_groupings, foods=None):
        Food.__init__(self, nutritional_groupings)
        self.foods = []
        if foods is not None:
            for food in foods:
                self.add(food)
    def _add_helper(self, first, second):
        # needed to deal with the default None's
        # used by add (only)
        if second is None:
            if first is None:
                return None
            else:
                return first
        elif first is None:
            return second
        else:
            return first + second
    def add(self, food):
        ## this can be looped using __dict__'s but it isn't very clear
        ## variable name "food" is unclear, maybe change
        self.foods.append(food) ## (!) now keeping the entire food object (!)
        for group in self.nutritional_groupings:
            for key in self.__dict__[group]:
                new_val = self._add_helper(self.get_val(group,key),
                                           food.get_val(group,key))
                self.__dict__[group][key] = new_val
                
    def with_(self, food):
        """ with_ is a non-mutating version of add that returns a new Meal
            object.  The underscore avoids conflicts with the "with" built-in.
            """
        new_obj = copy.deepcopy(self)
        new_obj.add(food)
        return new_obj

    def _subtract_helper(self, first, second):
        # needed to deal with all the default None's floating around
        # used by _sub_diff_helper (only)
        if first is None:
            if second is None:
                return None
            else:
                return 0 - second
        else:
            if second is None:
                return first
            else:
                if first - second > .000000001:
                    return first - second
                else:
                    return 0
    def _sub_diff_helper(self, food):
        # used by the subtract() and difference() methods

        for group in self.nutritional_groupings:
            for key in self.__dict__[group]:
                new_val = self._subtract_helper(self.get_val(group,key),
                                                food.get_val(group,key))
                self.__dict__[group][key] = new_val

    def subtract(self, food_name):
        """ Subtracts a food and its nutrients from the current meal.
            Unlike "difference()" this method causes data mutatation
            """
        assert food_name in [f.name for f in self.foods]
        for food in self.foods:
            if food.get_name() == food_name:
                self._sub_diff_helper(food)
                self.foods.remove(food)
                break
    
    def difference(self, food):
        """ Returns a Meal object that represents the DIFFERENCE between
            the meal (self) and another meal, which may just be a benchmark.
            """
        diff = copy.deepcopy(self)
        diff._sub_diff_helper(food)
        diff.foods = None # because this list is meaningless now 
        return diff
    def greater_than(self, food):
        """ Compares this meal to another meal, returns True iff every nutrient
            in this meal is greater than (or wins by default against) every
            nutrient in the meal passed in as an argument.

            In other words, the inputted meal must have at least one nutrient
            in its dictionaries with a value greater than this meal to return
            False.
            """
        assert type(food) in [Food, Meal]
        assert sorted(self.nutritional_groupings) == \
               sorted(food.nutritional_groupings)
        ## --check for logic error possibilities with None's--
        for group in self.nutritional_groupings:
            for key in self.__dict__[group]:
                this, that = self.get_val(group, key), food.get_val(group, key)
                if this < that:
                    if this is not None and that is not None:
                        return False
        return True
    
    def display_foods(self):
        if self.foods == []:
            return False
        print ''
        print 'Component Foods'
        print '-------------------------------------------------------------------------------'
        print "%-60s %15s" % ('Food Name', 'No. Servings')
        print '-------------------------------------------------------------------------------'
        for member in set(self.foods):
            if len(member) < 60:
                print "%-60s %15s" % (member,
                                      str(self.foods.count(member)).ljust(8))
            if len(member) > 59:
                print "%-60s %15s" % ((member[:57]+"..."),
                                      str(self.foods.count(member)).ljust(8))
        print '-------------------------------------------------------------------------------'
    def get_foods(self):
        return [food.get_name() for food in self.foods]

    def get_servings_and_foods(self):
        return [str(food.serving_size)+'g'+'--'+ food.get_name()
                for food in self.foods]

    def get_food_by_name(self, name):
        for food in self.foods:
            if food.get_name(name) == name:
                return food
        return False

def display_nutrients(food, min_meal, max_meal):
    """ Displays the nutritional contents of 3 meals.
        """
    ## you can put any three meals in here and they'll print in order
    ## ideal for food, min_meal, max_meal.  the GUI will do this now, but in
    ## case you want to see it in text...this is here
    print ''
    print 'Food/Meal Object: ', food.name
    for g in food.nutritional_groupings: # nutrient groupings (elements, vitamins, etc)
        print '-------------------------------------------------------------------'
        print 'Group:', g   #, 'food.d(g):', food.d(g)
        print "%-35s %-10s %-10s %-10s" % ('Name', 'Meal', 'Min', 'Max')
        print '-------------------------------------------------------------------'
        for key in food.d(g):
            print "%-35s %-10s %-10s %-10s" % (key,
                                               food.d(g)[key],
                                               min_meal.d(g)[key],
                                               max_meal.d(g)[key])

def display_info(food):
    d_min = make_daily_min(food.nutritional_groupings)
    d_max = make_daily_max(food.nutritional_groupings)
    display_nutrients(food, d_min, d_max)

def info(name):
    food = get_food_with_name(name)
    display_info(food)
    print 'weight:', food.serving_size, 'grams'

#############################################################################
############################ nutritional benchmarks #########################
#############################################################################
# *see nutrient_subgroups.py

def make_daily_min(groupings):
    # not complete
    assert type(groupings) == list
    daily_min = Meal(groupings)
    if 'elements' in groupings:
        daily_min.elements['Sodium, Na'] = 1500.
        daily_min.elements['Phosphorus, P'] = 700.
        daily_min.elements['Manganese, Mn'] = 2.3
        daily_min.elements['Iron, Fe'] = 8. 
        daily_min.elements['Potassium, K'] = 4700.
        daily_min.elements['Fluoride, F'] = None #4. having troubles
        daily_min.elements['Selenium, Se'] = None #.055 having troubles, units off?
        daily_min.elements['Magnesium, Mg'] = 420.
        daily_min.elements['Zinc, Zn'] = 11.
        daily_min.elements['Copper, Cu'] = .9
        daily_min.elements['Calcium, Ca'] = 1000.
    if 'vitamins' in groupings:
        daily_min.vitamins['Niacin'] = 16.
        daily_min.vitamins['Thiamin'] = 1.2
        daily_min.vitamins['Vitamin B-6'] = None ## instead of zero?
        daily_min.vitamins['Pantothenic acid'] = 5.
        daily_min.vitamins['Vitamin C, total ascorbic acid'] = 90.
        daily_min.vitamins['Vitamin A, IU'] =.9
        daily_min.vitamins['Vitamin E (alpha-tocopherol)'] = 15.
        daily_min.vitamins['Vitamin D'] = .015
        daily_min.vitamins['Folate, total'] = .4 
        daily_min.vitamins['Vitamin B-12'] = .0024
        daily_min.vitamins['Vitamin K (phylloquinone)'] = .12
    if 'amino_acids' in groupings:
        # assumed to be per 100kg, source for Proof Of Concept from
        # http://en.wikipedia.org/wiki/Essential_amino_acid#Recommended_daily_amounts
        # Methionine+Cysteine and Phenylalanine+Tyrosine were broken up,
        # although they are substitutes for eachother.  These are in a sense
        # dummy values!!!
        daily_min.amino_acids['Lysine'] = 3000
        daily_min.amino_acids['Phenylalanin'] = 1250
        daily_min.amino_acids['Leucine'] = 3900
        daily_min.amino_acids['Methionine'] = 750
        daily_min.amino_acids['Histidine'] = 1000
        daily_min.amino_acids['Valine'] = 2600
        daily_min.amino_acids['Tryptophan'] = 400
        daily_min.amino_acids['Isoleucine'] = 2000
        daily_min.amino_acids['Threonine'] = 1500
        daily_min.amino_acids['Cystine'] = 750
        daily_min.amino_acids['Tyrosine'] = 1250 
    return daily_min

def make_daily_max(groupings):
    assert type(groupings) == list
    daily_max = Meal(groupings)
    if 'elements' in groupings:
        daily_max.elements['Sodium, Na'] = 2300.
        daily_max.elements['Phosphorus, P'] = 4000.
        daily_max.elements['Manganese, Mn'] = 211.
        daily_max.elements['Iron, Fe'] = 45.
        daily_max.elements['Potassium, K'] = 999999. ## 999999. means no upper limit
        daily_max.elements['Fluoride, F'] = None #10.  having troubles
        daily_max.elements['Selenium, Se'] = None #.4 having troubles, units off?
        daily_max.elements['Magnesium, Mg'] = 999999.
        daily_max.elements['Zinc, Zn'] = 40.
        daily_max.elements['Copper, Cu'] = 10.
        daily_max.elements['Calcium, Ca'] = 2500.
    if 'vitamins' in groupings:
        daily_max.vitamins['Niacin'] = 35.
        daily_max.vitamins['Thiamin'] = 999999. 
        daily_max.vitamins['Vitamin B-6'] =  100.
        daily_max.vitamins['Pantothenic acid'] = 999999.
        daily_max.vitamins['Vitamin C, total ascorbic acid'] = 2000. 
        daily_max.vitamins['Vitamin A, IU'] = 3.
        daily_max.vitamins['Vitamin E (alpha-tocopherol)'] = 1000.
        daily_max.vitamins['Vitamin D'] = .05
        daily_max.vitamins['Folate, total'] = 1. 
        daily_max.vitamins['Vitamin B-12'] = 999999.
        daily_max.vitamins['Vitamin K (phylloquinone)'] = 999999. 
    return daily_max


amino_acid_per_mass = {'Lysine': 3000, 'Alanine': None,
                                'Glycine': None, 'Proline': None, 'Serine': None,
                                'Arginine': None, 'Glutamic acid': None,
                                'Phenylalanine': 1250, 'Leucine': 3900,
                                'Methionine': 750, 'Histidine': 1000,
                                'Valine': 2600, 'Tryptophan': 400,
                                'Isoleucine': 2000, 'Threonine': 1500,
                                'Aspartic acid': None, 'Cystine': 750,
                                'Tyrosine': 1250}

def add_amino_acids_to_min(daily_min, body_weight):
    # body_weight is assumed to be in kilograms
    for element in daily_min.amino_acids:
        daily_min.amino_acids[element] = amino_acid_per_mass[element] * \
                                         (body_weight / 100)
    return daily_min
    
def add_amino_acids_to_max(daily_max, body_weight):
    # no max info at this time
    pass
    

#############################################################################
########################### JSON considerations #############################
#############################################################################

## JSON (list)
##  -objects (dictionary)
##      -'portions' (key)
##          -list
##              -'amount' (key)
##              -'grams' (key)
##              -'units' (key)
##      -'description' (key)
##          string value (value)
##      -'tags' (key)
##          bunch of random stuff, *could* be useful for search? (list)
##      -'nutrients'
##          * see nutrient subgroups
##      -'group' (key)
##          food group string (value)
##      -'id' (key)
##          integer (value)
##      -'manufacturer' (key)
##          string (68 in total for the entire db) (value)

##
## JSON filters (these filter foods *before* they're mapped into the custom
##               Food objects)

class Food_Group_Filter(object):
    def __init__(self, name_list=None):
        ## to use initialize with a list of some or all of the keys from
        ## the dictionary below
        self.d = {'Dairy and Egg Products':0, 'Spices and Herbs':0,\
             'Baby Foods':0, 'Fats and Oils':0, 'Poultry Products':0,\
             'Soups, Sauces, and Gravies':0, 'Sausages and Luncheon Meats':0,\
             'Breakfast Cereals':0,'Fruits and Fruit Juices':0,\
             'Pork Products':0, 'Vegetables and Vegetable Products':0,\
             'Nut and Seed Products':0,'Beef Products':0, 'Beverages':0,\
             'Finfish and Shellfish Products':0,\
             'Legumes and Legume Products':0, 'Lamb, Veal, and Game Products':0,\
             'Baked Products':0, 'Snacks':0, 'Sweets':0,
             'Cereal Grains and Pasta':0,'Fast Foods':0,\
             'Meals, Entrees, and Sidedishes':0, 'Ethnic Foods':0,\
             'Restaurant Foods':0}
        if name_list is not None:
            for name in name_list:
                self.d[name] = 1
        else:
            # default to all groups included if no groups supplied
            for k in self.d:
                self.d[k] = 1
    def check(self, group):
        if self.d[group] == 1:
            return True
        else:
            return False
    def get_groups(self):
        return [x for x in self.d if self.d[x] == 1]

class Name_Filter(object):
    def __init__(self, name_list=None):
        if name_list is not None:
            self.n = name_list
        else:
            self.n = []
    def check(self, name):
        # if no names supplies filter defaults to True
        if self.n == []:
            return True
        elif name in self.n:
            return True
        else:
            return False

def get_all_groups():
    """ Gathers the different food groups from the database, only used for
        db exploration, i.e. making the group filter template.
        """
    global db_tuple
    groups = []
    error_count = 0
    for jdict in db_tuple:
        if jdict['group'] not in groups:
            groups.append(jdict['group'])
    if debugging: print error_count, "objects had troubles and were skipped"
    return groups


## 1441 objects skipped, but from the rest the groups were:
## will need to investigate those 1441 objects (ascii errors? i.e. 2% milk)
the_groups = ['Dairy and Egg Products', 'Spices and Herbs', 'Baby Foods',\
              'Fats and Oils', 'Poultry Products', 'Soups, Sauces, and Gravies',\
              'Sausages and Luncheon Meats', 'Breakfast Cereals',\
              'Fruits and Fruit Juices', 'Pork Products',\
              'Vegetables and Vegetable Products', 'Nut and Seed Products',\
              'Beef Products', 'Beverages', 'Finfish and Shellfish Products',\
              'Legumes and Legume Products', 'Lamb, Veal, and Game Products',\
              'Baked Products', 'Snacks', 'Sweets', 'Cereal Grains and Pasta',\
              'Fast Foods', 'Meals, Entrees, and Sidedishes', 'Ethnic Foods',\
              'Restaurant Foods']

## a filter for groups (0 for discard, 1 for keep):
## ** this is used for filtering JSON objects before they get mapped in **

basic_filter = Food_Group_Filter(['Fats and Oils', 'Soups, Sauces, and Gravies',
                              'Breakfast Cereals', 'Fruits and Fruit Juices',
                              'Vegetables and Vegetable Products',
                              'Nut and Seed Products', 'Beverages',
                              'Legumes and Legume Products', 'Baked Products',
                              'Snacks', 'Sweets', 'Cereal Grains and Pasta',
                              'Meals, Entrees, and Sidedishes'])

all_groups_filter = Food_Group_Filter(the_groups)
        
veggie_filter = Food_Group_Filter(['Vegetables and Vegetable Products',
                              'Nut and Seed Products'])
veggie_beef_filter = Food_Group_Filter(['Vegetables and Vegetable Products',
                                   'Nut and Seed Products',
                                   'Beef Products'])
                                   
# this is a filter to pick a subset of the vegetable group, names are just
# copy/pasted from the output of the get_veggies funtion that output 872 veggies
# many of which are basically the same thing, so this narrows it down a bit
# ** this search could be done marginally more quickly using id's instead of
# descriptions, but descriptions make it so looking at the filter is more easily
# readable
veggie_name_filter = ['Alfalfa seeds, sprouted, raw', 'Amaranth leaves, raw',
                      'Artichokes, (globe or french), raw',
                      'Asparagus, raw', 'Bamboo shoots, raw', 'Beets, raw',
                      'Broccoli, raw', 'Brussels sprouts, raw',
                      'Lentils, sprouted, cooked, stir-fried, without salt',]

def get_food_from_group_by_name(group_filter, name):
    """ Given a name and a filter of the group that name is in, returns the
        single corresponding object.
        """
    ## this should be optimized later (should terminate when object is found)
    assert type(group_filter) is Food_Group_Filter and type(name) is str
    return get_foods_by_group_and_name(group_filter, Name_Filter([name]))[0]


##
## JSON data
## 

## hopefully this is enough to keep this working, when packaged under py2exe
## this is a little more complicated than one mught guess.
## this little chunk must be coordinated with setup.py for the program to run
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
json_loc = os.path.join(current_dir, "foods-2011-10-03.json")
jsonfile = open(json_loc, "r")

db_tuple = tuple(json.load(jsonfile)) # tuple to prevent mutation

def get_filtered_object_count(the_filter):
    """ Counts the number of objects that can successfully be retrieved from
        the JSON database as constrained by the_filter
        """
    count = 0
    for jdict in db_tuple:
        if the_filter.check(jdict["group"]):
            count += 1
    return count

def get_filtered_object_names(the_filter):
    """ Gets the names of the objects that can be successfully retrieved from
        the JSON database as constrained by the_filter
        """
    food_names = []
    for jdict in db_tuple:
        if the_filter.check(jdict["group"]):
            food_names.append(jdict["description"])
    return food_names

def get_objects_by_group_and_name(group_filter, name_filter):
    """ Steps through the JSON database and keeps objects that satisfy the
        group and name filters' constraints.
        """
    global db_tuple
    assert type(group_filter) is Food_Group_Filter and \
           type(name_filter) is Name_Filter
    objects = []
    
    for jdict in db_tuple:
        if group_filter.check(jdict['group']) and\
           name_filter.check(jdict['description']):
            objects.append(jdict)
    return objects

def get_object_by_name(name):
    """ Steps through the JSON database and returns the first object that meets
        the name criteria.
        """
    for jdict in db_tuple:
        if name == jdict['description']:
            return jdict
    return False

import re
def search_by_name(word):
    matches = []
    # db_tuple is the 'global' database, (not mutated so not declared)
    for jdict in db_tuple:
        if re.search(word.lower(),
                      jdict['description'].lower()) is not None:
            matches.append(jdict['description'])
    return matches

def search_many(word_list):
    # a fairly naive multiple term search algorithm (term grouping is not incl.)
    # counts the matches for each description, must match at least all but one
    # term in the word list
    matches = {}
    for jdict in db_tuple: # db_tuple is the database, jdict is a json object
        for word in word_list:
            if re.search(word.lower(),
                      jdict['description'].lower()) is not None:
                if jdict['description'] not in matches.keys():
                    matches[jdict['description']] = 1
                else:
                    matches[jdict['description']] += 1
    intermediate = sorted(matches.items(), key=lambda x: x[1], reverse=True)
    return [x[0] for x in intermediate if x[1] >= len(word_list) - 1
            and x[1] > 1]
            
 


#############################################################################
######################## From JSON to Food objects ##########################
#############################################################################

def get_food_objects(food_group_filter=Food_Group_Filter(),
                     name_filter=Name_Filter(),
                     nutrient_group_filter=['elements', 'vitamins']):
    """ Given group, name and nutrient group filters, finds corresponding
        objects from the JSON database and maps them into Food objects,
        returns a list of Food objects.
        """
    obj_list = get_objects_by_group_and_name(food_group_filter, name_filter)
    return [Food(nutrient_group_filter, obj) for obj in obj_list]

def get_foods_for_objects(objects, nutrient_groups=['vitamins', 'elements',
                                                    'amino_acids']):
    return [Food(nutrient_groups, obj) for obj in objects]

def get_food_with_name(food_name, nutrient_groups=None):
    ######## rewrite
    if nutrient_groups == None:
        nutrient_groups = ['elements', 'vitamins', 'amino_acids']
    the_object = get_object_by_name(food_name)
    if the_object is not False:
        return Food(nutrient_groups, the_object)
    else:
        return False


#############################################################################
############################## GUI Specific #################################
#############################################################################

## all GUI communication with what's above thie line takes place below this line
## (except for methods included in Meal and Food objects)

def get_fields(nutritional_groupings=['elements', 'vitamins', 'energy',
                                      'sugars', 'amino_acids', 'other',
                                      'composition']):
    print 'get_fields groupings:', nutritional_groupings
    food = Food(nutritional_groupings)
    fields = dict()
    for group in food.nutritional_groupings:
        fields[group] = food.__dict__[group].keys()
    return fields

def get_fields_for_group(group):
    food = Food([group])
    fields = food.__dict__[group].keys()
    return fields

def get_food(name, groupings=['elements', 'vitamins', 'energy', 'sugars',
                              'amino_acids', 'other', 'composition']):
    """ Takes a food name (string) and returns the corresponding Food object.
        """
    return get_food_with_name(name, groupings)

def get_meal(name_list, groupings=['elements', 'vitamins', 'energy',
                                      'sugars', 'amino_acids', 'other',
                                      'composition']):
    """ Takes a list of food names (strings) and returns a Meal object of
        those foods.
        """
    meal = Meal(groupings)
    for name in name_list:
        food = get_food_with_name(name)
        meal.add(food)
    return meal

def get_benchmarks(nutritional_groupings=['elements', 'vitamins', 'energy',
                                      'sugars', 'amino_acids', 'other',
                                      'composition']):
    """ Returns a two-tuple of the minimum and maximum daily allowances
        """
    return (make_daily_min(nutritional_groupings),
            make_daily_max(nutritional_groupings))
    
def search_like(search_string):
    assert type(search_string) is unicode or type(search_string) is str
    search_list = search_string.split(' ')
    if len(search_list) == 1:
        return search_by_name(search_string)
    else:
        return search_many(search_list)

