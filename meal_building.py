## The Perfect Meal
## Author: Christopher Olsen
## Copyright: 2013
##
## This port (windows) under temporary copyright.  The GNU/Linux branch is
## under the GPLv3.


## This file holds algorithms for searching for meals that satisfy arbitrary
## nutritional constraints

## **** THIS FILE NEEDS CLEANUP AND WORK **** (it's not very clear or workable)

#############################################################################
############################### FINDING MEALS ###############################
#############################################################################

import perfectmeal as perfect_meal

def greedy_alg(min_meal, max_meal, servings, food_groups, nutrient_groups,
                   comparator, seed_name=None, seed_meal=None, names=None):
    """ 
        min_meal: benchmark Meal object
        max_meal: benchmark Meal object
        servings: integer
        food_groups: list, used to filter from the JSON database
        nutrient_groups: list, used as an argument for Food and Meal objects
        comparator: procedure, comparator used to measure objects
        seed_name: list of names used as a seed
        seed_meal: meal to be used as a seed
        names: (???) optional list of food names, filters the JSON objects             """
    #print 'Greedy Algorithm Beginning, comparator is:', comparator.__name__
    foods = perfect_meal.get_food_objects(food_groups,
                                          perfect_meal.Name_Filter(names),
                             nutrient_groups)
    if seed_meal is not None:
        current_meal = seed_meal
        current_foods = seed_meal.foods
    else:
        first_food = perfect_meal.get_food_with_name(seed_name, nutrient_groups)
        current_foods = [first_food]
        #tries = [first_food]
        current_meal = perfect_meal.Meal(nutrient_groups, first_food)
    counter = [0] # putting the counter in a list sidesteps namespace
                  # issues (nonlocal not implemented until Python 3.0)
    def _next_food_helper(current_meal, min_meal, max_meal, foods,
                          nutrient_groups, comparator):
        """
            current_meal: the meal so far
            min_meal, max_meal: the benchmark meals
            foods: list of Food objects from above
            nutrient_groups: i.e. ['vitamins', 'elements']
            comparator: function that takes a meal, the min_meal and an
                        optional argument
                        returns a unitless number, smaller = better
            """
        next_food = foods[0] # seed
        next_food_meal_score = comparator(min_meal,
                                          current_meal.with_(next_food),
                                          counter)
        for food in foods:
            prospective_meal_score = comparator(min_meal,
                                                current_meal.with_(food),
                                                counter)
            if not max_meal.greater_than(current_meal.with_(food)):
                continue  ## where is the best place for this check???
            if prospective_meal_score < next_food_meal_score:
                next_food = food
                next_food_meal_score = prospective_meal_score
        counter[0] += 1
        #print 'next food is:', next_food.name
        return next_food
    
    while len(current_foods) < servings:
        if not max_meal.greater_than(current_meal):
            print "Dead end reached in search algorithm, one or more"
            print "maximum constraints have been violated"
            print "Current foods: ", [x.name for x in current_foods]
            return current_meal
        if current_meal.greater_than(min_meal):
            return current_meal
        current_foods.append(_next_food_helper(current_meal, min_meal,
                                               max_meal, foods,
                                               nutrient_groups, comparator))
        current_meal.add(current_foods[-1])
    return current_meal


## COMPARATORS (return a unitless number used to compare meals)
    ## the 'optional' argument can be used to pass whatever info may be needed
    ## it may be nice to include a lambda function with each comparator that
    ## will automatically gather whatever info that comparator may need
    
def finish_line(min_meal, meal, optional=None):
    """ This algorithm takes a meal and a min_meal (benchmark meal) and finds
        the total distance between the meal and meeting its min constraints.
        The bigger the distance the farther from the min-meal.
        """
    distance = 0
    for group in meal.nutritional_groupings:
        for key in meal.d(group):
            if meal.d(group)[key] < min_meal.d(group)[key]:
                if meal.d(group)[key] is not None and\
                   min_meal.d(group)[key] is not None: ## temporary, better way?
                    distance += ((min_meal.d(group)[key] -
                                  meal.d(group)[key]) / min_meal.d(group)[key])
    return distance

def balance(min_meal, meal, optional=None):
    """ This algorithm focuses on the overall balance of a meal, the more
        evenly distributed the nutrients, the lower the b_factor.
        If every nutrient is at 80% of it's min value the b_factor would be
        zero, this only measures lopsidedness.
        The bigger the number the more lopsided the meal.
        """
    total = 0 # total distance from perfect balance
    count = 0
    # get the average level
    for group in meal.groupings:
        for key in meal.d(group):
            if meal.d(group)[key] is not None and\
                   min_meal.d(group)[key] is not None:
                total += meal.d(group)[key] / min_meal.d(group)[key]
                count += 1
    average = total/count
    b_factor = 0
    for g in meal.groupings:
        for key in meal.d(group):
            if meal.d(group)[key] is not None and\
                   min_meal.d(group)[key] is not None: ## temporary
                #b_factor += abs(average - (meal.d(group)[key] / min_meal.d(group)[key]))
                if meal.d(group)[key] < min_meal.d(group)[key]:
                    b_factor += 4 * abs(average - (meal.d(group)[key] / min_meal.d(group)[key]))
                else:
                    b_factor += abs(average - (meal.d(group)[key] / min_meal.d(group)[key]))
    return b_factor
    
def alternating_finish_line_balance(min_meal, meal, optional=None):
        # BROKEN. Why is a list getting passed in for optional???
    if optional % 2 == 0:
        return balance(min_meal, meal, optional)
    else:
        return finish_line(min_meal, meal, optional)


def test_greedy_finish_line(seed='Alfalfa seeds, sprouted, raw'):
    groupings = ['elements', 'vitamins']
    d_min = perfect_meal.make_daily_min(groupings)
    d_max = perfect_meal.make_daily_max(groupings)
    the_meal = greedy_alg(d_min, d_max, 250, perfect_meal.veggie_beef_filter,
                          groupings, finish_line,
                          seed)
    perfect_meal.display_nutrients(the_meal, d_min, d_max)
    print "Meets minimum requirements? ", the_meal.greater_than(d_min)
    print "Meets maximum requirements? ", d_max.greater_than(the_meal) 
    return the_meal

def greedy_finish_with_meal(the_meal):
    d_min = perfect_meal.make_daily_min(the_meal.nutritional_groupings)
    d_max = perfect_meal.make_daily_max(the_meal.nutritional_groupings)
    return greedy_alg(d_min, d_max, 250, perfect_meal.veggie_beef_filter,
                      the_meal.nutritional_groupings, finish_line,
                      seed_meal=the_meal)
    

def test_greedy_balance(seed='Alfalfa seeds, sprouted, raw'):
    ## this takes a very long time to run and doesn't return a valid solution
    ## for 1000 foods it still doesn't reach all minimum values
    ## perhaps some sort of weighting scheme will help?
    groupings = ['elements', 'vitamins', 'amino_acids']
    d_min = perfect_meal.make_daily_min(groupings)
    d_max = perfect_meal.make_daily_max(groupings)
    the_meal = greedy_alg(d_min, d_max, 10000, perfect_meal.veggie_beef_filter,
                          groupings, balance,
                          seed)
    display_nutrients(the_meal, d_min, d_max)
    print "Meets minimum requirements? ", the_meal.greater_than(d_min)
    print "Meets maximum requirements? ", d_max.greater_than(the_meal) 
    return the_meal

def test_greedy_alternating(seed='Alfalfa seeds, sprouted, raw'):
    groupings = ['elements', 'vitamins']
    d_min = perfect_meal.make_daily_min(groupings)
    d_max = perfect_meal.make_daily_max(groupings)
    the_meal = greedy_alg(d_min, d_max, 250, perfect_meal.veggie_beef_filter,
                          groupings, alternating_finish_line_balance,
                          seed)
    display_nutrients(the_meal, d_min, d_max)
    print "Meets minimum requirements? ", the_meal.greater_than(d_min)
    print "Meets maximum requirements? ", d_max.greater_than(the_meal) 
    return the_meal
            
def run_walk_greedy_alg():
    """ Uses the finish_line() comparator until half of the nutrients have met
        their min constraints, then switches to the balance() comparator.
        """
    pass

def balanced_walk_greedy_alg():
    """ Uses the finish_line() comparator unless the nutritional balance is
        too unbalanced, then uses balance() to balance the situation before
        switching back to finish_line()
        """
    pass
