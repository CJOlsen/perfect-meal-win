## The Perfect Meal
## Author: Christopher Olsen
## Copyright: 2013
## License: GNU GPL v3
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

import ackpl # the Arbitrary Constraint Knapsack Problem Library
import threading
from multiprocessing.pool import ThreadPool
import json
import re
import os # to find current directory (to find the json database)
import sys # same, used if the os method fails

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
        ## For comparisons to work the nutritional_groupings list will need to
        ## be the same for all Foods being used - problematic
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
                                'Tyrosine': None, 'Hydroxyproline': None}
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
        ## ** marked for deprecation or full implementation
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

    def flatten(self):
        """ Flattens the active nutritional groupings into one dictionary."""
        flat = {}
        for group in self.nutritional_groupings:
            first_dict = flat.items()
            second_dict = self.__dict__[group].items()
            flat = dict(first_dict + second_dict)
            #flat = dict(flat.items() + self[group].items())
        return flat
    
    @classmethod
    def unflatten(cls, dictionary, name):
        """ Unflattens the food.  Actually creates a new Food object and populates
            its values from the provided dictionary. """
        ## ** this needs to be cleaned up
        keys = dictionary.keys()
        # create the food with all nutritional groups
        new_food = Food(['elements', 'vitamins', 'energy', 'sugars',
                         'amino_acids', 'other', 'composition'], name=name)
        # populate the nutritional groups
        for group in new_food.nutritional_groupings:
            for item_name in new_food.__dict__[group]:
                if item_name in dictionary.keys():
                    new_food.__dict__[group][item_name] = dictionary[item_name]
        # remove the extra nutritional groups (not clear or efficient)
        for group in new_food.nutritional_groupings:
            if set(new_food.__dict__[group].keys()) <= set(dictionary.keys()):
                # the nutritional group's keys are all in the dictionary
                pass
            else:
                del new_food.__dict__[group]
        return new_food
            
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
        daily_min.amino_acids['Phenylalanine'] = 1250
        daily_min.amino_acids['Leucine'] = 3900
        daily_min.amino_acids['Methionine'] = 750
        daily_min.amino_acids['Histidine'] = 1000
        daily_min.amino_acids['Valine'] = 2600
        daily_min.amino_acids['Tryptophan'] = 400
        daily_min.amino_acids['Isoleucine'] = 2000
        daily_min.amino_acids['Threonine'] = 1500
        daily_min.amino_acids['Cystine'] = 750
        daily_min.amino_acids['Tyrosine'] = 1250
        daily_min.amino_acids['Hydroxyproline'] = 5 
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
        ## ** this needs to be deprecated or implemented more fully
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

## json needs to be loaded using multithreading/multiprocessing so it doesn't
## hold up the entire program.  The multithreading approach is being
## experimented with bnut my computer only has one processor so I can't run
## and debug the multithreaded solution

db_tuple = tuple(json.load(jsonfile)) # tuple to prevent mutation


## database in pieces, separated by food group
def make_database_by_foodgroup(full_db):
    """ Create a dictionary from the json database where the keys are food
        groups and the values are lists of their members.

        Useful for searching through part of the database.
        """
    food_groups = ['Dairy and Egg Products', 'Spices and Herbs', 'Baby Foods',\
                  'Fats and Oils', 'Poultry Products', 'Soups, Sauces, and Gravies',\
                  'Sausages and Luncheon Meats', 'Breakfast Cereals',\
                  'Fruits and Fruit Juices', 'Pork Products',\
                  'Vegetables and Vegetable Products', 'Nut and Seed Products',\
                  'Beef Products', 'Beverages', 'Finfish and Shellfish Products',\
                  'Legumes and Legume Products', 'Lamb, Veal, and Game Products',\
                  'Baked Products', 'Snacks', 'Sweets', 'Cereal Grains and Pasta',\
                  'Fast Foods', 'Meals, Entrees, and Sidedishes', 'Ethnic Foods',\
                  'Restaurant Foods']
    data_dict = {x:[] for x in food_groups}
    for item in full_db:
        data_dict[item['group']].append(item)
    return data_dict

db_by_foodgroup = make_database_by_foodgroup(db_tuple)

def get_partial_db(food_groups):
    total = []
    for key in food_groups:
        total += db_by_foodgroup[key]
    return total

########################################

def get_objects_by_group_and_name(food_group_filter, name_filter):
    """ Steps through the JSON database and keeps objects that satisfy the
        group and name filters' constraints.
        """
    ## TODO: fix this to work with get_partial_db()

    #print ''
    #print 'food_group_filter and name_filter', food_group_filter, name_filter
    #print ''
    assert type(food_group_filter) is Food_Group_Filter
    # and type(name_filter) is Name_Filter
    objects = []

    partial = get_partial_db(food_group_filter.get_groups())
    
    for jdict in partial:
        if food_group_filter.check(jdict['group']) and\
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

def search_by_name(word, food_groups):
    matches = []
    # db_tuple is the 'global' database, (not mutated so not declared)
    partial_db = get_partial_db(food_groups)
    for jdict in partial_db:
        if re.search(word.lower(),
                     jdict['description'].lower()) is not None:
            matches.append(jdict['description'])
    return matches

def search_many(word_list, food_groups):
    # a fairly naive multiple term search algorithm (term grouping is not incl.)
    # counts the matches for each description, must match at least all but one
    # term in the word list
    partial_db = get_partial_db(food_groups)
    matches = {}
    for jdict in partial_db: # partial_db is the database, jdict is a json object
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
    #print 'get_food_objects, type(name_filter', type(name_filter)
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
    #print 'get_fields groupings:', nutritional_groupings
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
    
def search_like(search_string, food_groups):
    assert type(search_string) is unicode or type(search_string) is str
    assert type(food_groups) is list
    search_list = search_string.split(' ')
    if len(search_list) == 1:
        return search_by_name(search_string, food_groups)
    else:
        return search_many(search_list, food_groups)
    
def get_available_algs():
    """ Go-between for the GUI and ackpl """
    # this exists so perfectmeal_gui doesn't need to directy access ackpl.py
    return ackpl.algorithm_names()

def complete_meal(current_meal, min_meal, max_meal, algorithm, food_groups):
    """ Acts as a go-between for the GUI and ackpl.py
        Returns a "completed" meal, completed either because it violated a max
        constraint or because it satisfied all of its min constraints.
        """
    ## should this Name_Filter class be derprecated or just renamed?
    all_foods = get_food_objects(food_group_filter=Food_Group_Filter(food_groups),
                                 name_filter=Name_Filter(),
                                 nutrient_group_filter=current_meal.nutritional_groupings)
    possibilities = []
    serving_sizes = {}
    for food in all_foods:
        serving_sizes[food.get_name()] = food.serving_size
        possibilities.append([food.get_name(), food.flatten()])
    minimums = ('minimums', min_meal.flatten())
    maximums = ('maximums', max_meal.flatten())
    currents = [[food.name, food.flatten()] for food in current_meal.foods]
    #algorithm = algorithm

    completed_flat = ackpl.ackp(possibilities, minimums, maximums, currents, 
                                algorithm)
    if completed_flat is None:
        return None
    if type(completed_flat) is not list:
        return completed_flat ## maybe?
    foods = []
    for food in completed_flat:
        new_food = Food.unflatten(food[1], food[0])
        new_food.serving_size = serving_sizes[new_food.get_name()]
        foods.append(new_food)
    #print 'number foods', len(foods)
    new_meal = Meal(foods[0].nutritional_groupings, foods)
    return new_meal

def get_all_foodgroups():
    # pulling from a global?  this could be better...
    return the_groups

