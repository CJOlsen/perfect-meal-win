## Arbitrary Constraint Knapsack Problem Library
## Author: Christopher Olsen
## Copyright: 2013
## License: GNU GPL v3
##

## This is a library to handle knapsack problems with arbitrary constraints, 
## including having both max and min.  This is being made with my Perfect Meal
## program in mind but I'd like to spin this piece off as its own little thing

debug = False

def algorithm_names():
    """ Return a list of different algorithm options """
    return ["greedy_balance","greedy_balance_pickonce",
            "greedy_finishline","greedy_finishline_pickonce",
            "greedy_alternating","greedy_alternating_pickonce",
            "greedy_runwalk","greedy_runwalk_pickonce",]


def ackp(possibilities, minimums, maximums=None, currents=None, 
         algorithm="greedy_balance"):
    """ 
    Main interface function for the library.  Primarily a dispatch.

    possibilities: a list of two-tuples: name, dictionaries (keys are the 
                   constrained elements)
    minumums: a two-tuple: [name, dictionary of the minimum values each 
              constrained element must reach]
    maximums: a two-tuple: [name, dictionary of the maximun values each 
              constrained element can reach]
    currents: a list of two-tuples: [name, dictionary of constrained element 
              names and their values].  The current members of the knapsack.
    algorithm: if the user has a preference of algorithm it can be entered here
               currently defaults to "greedy_balance"
    """
    
    # quality checks (maybe add error messages)
    assert type(possibilities) is list
        # check contents of first member of possibilities
    assert type(possibilities[0][0]) is str or \
        type(possibilities[0][0]) is unicode
    assert type(possibilities[0][1]) is dict
    assert type(minimums) is tuple
    assert maximums is None or type(maximums) is tuple
    assert currents is None or type(currents) is list
      # check that all keys match
    assert set(possibilities[0][1].keys()) == set(minimums[1].keys())
    if maximums != None:
        assert set(possibilities[0][1].keys()) == set(maximums[1].keys())
    if currents != None:
        assert set(possibilities[0][1].keys()) == set(currents[0][1].keys())
    
    # dispatch
    if "greedy" in algorithm:
        if "greedy_balance" == algorithm:
            if debug: print 'calling greedy_alg'
            return greedy_alg(possibilities, minimums, maximums, currents, 
                              balance_indx) # balance_indx defined below
        elif "greedy_balance_pickonce" == algorithm:
            return greedy_alg(possibilities, minimums, maximums, currents, 
                              balance_indx, unique=True)
        elif "greedy_finishline" == algorithm:
            return greedy_alg(possibilities, minimums, maximums, currents, 
                              finishline_indx)
        elif "greedy_finishline_pickonce" == algorithm:
            return greedy_alg(possibilities, minimums, maximums, currents, 
                              finishline_indx, unique=True)
        elif "greedy_alternating"  == algorithm:
            return greedy_alg(possibilities, minimums, maximums, currents, 
                              alternating_indx)
        elif "greedy_alternating_pickonce"  == algorithm:
            return greedy_alg(possibilities, minimums, maximums, currents, 
                              alternating_indx, unique=True)
        elif "greedy_runwalk"  == algorithm:
            return greedy_alg(possibilities, minimums, maximums, currents, 
                              runwalk_indx)
        elif "greedy_runwalk_pickonce"  == algorithm:
            return greedy_alg(possibilities, minimums, maximums, currents, 
                              runwalk_indx, unique=True)
        else:
            return NotImplemented

    elif "super awesome whatever" in algorithm:
        ## todo. non-greedy algorithms.  should be interesting....
        pass
    else:
        if debug: print 'no algorithm match found'
        return None

## helper functions
def dict_greater(dict1, dict2):
    """ Determines if *all* values in dict1 are greater than their 
        corresponding values in dict2
        """
    for key in dict1.keys():
        dict1_val, dict2_val = dict1[key], dict2[key]
        if dict1_val < dict2_val:
            if dict1_val is not None and dict2_val is not None:
                return False 
    return True # dict1 is greater

def dict_add(dict1, dict2):
    """ Adds two dictionaries together. """
    dict3 = {}
    for key in dict1.keys():
        dict1_val, dict2_val = dict1[key], dict2[key]
        if dict1_val is None:
            if dict2_val is None:
                dict3[key] = None
            else:
                dict3[key] = dict2_val
        else:
            if dict2_val is None:
                dict3[key] = dict1_val
            else:
                dict3[key] = dict1_val + dict2_val
    return dict3

def dict_sub(dict1, dict2):
    """ Subtracts dict2's values from dict1 """
    dict3 = {}
    for key in dict1.keys():
        dict1_val, dict2_val = dict1[key], dict2[key]
        if dict1_val is None:
            if dict2_val is None:
                dict3[key] = None
            else:
                dict3[key] = -dict2_val
        else:
            if dict2_val is None:
                dict3[key] = dict1_val
            else:
                dict3[key] = dict1_val - dict2_val
    return dict3


## Greedy Algorithms
def greedy_alg(possibilities, minimums, maximums, currents, indexer, 
               unique=False):
    """
    This is a greedy algorithm (i.e. continual local optimization)

    possibilities: a list of dictionaries of names (keys) and lists (values) 
                   of possible additions to the knapsack
    minumums: a dictionary of the minimum values each of them must reach
    maximums: a dictionary of the maximum values each of them can reach
    currents: a list of dictionaries the current values, must have same keys
    unique: False means a 'possibility' can be used more than once.  True means
            it will be removed from 'possibilities' once used
            """
    if debug: print 'greedy_alg...'
    # find current total
    if currents is not None:
        if len(currents) == 1:
            total = ['total', currents[0][1]]
        else:
            total = ['total', dict_add(currents[0][1], currents[1][1])]
            for curr in currents[2:]:
                total[1] = dict_add(total[1], curr[1])
    else:
        currents = []
        total = ['total', {}]
        for key in minimums[1]:
            total[1][key] = 0
            

    def _next_item_helper(possibilities):
        current_next = possibilities[0]
        current_score = indexer(minimums,
                                ['total', dict_add(total[1], current_next[1])],
                                currents)
        for poss in possibilities[1:]:
            poss_score = indexer(minimums,
                                 ['total', dict_add(total[1], poss[1])],
                                 currents)
            if poss_score < current_score:
                current_next = poss
                current_score = poss_score
        if unique == True:
            possibilities.remove(current_next)
        return current_next
    if debug: print 'pre while loop'
    i = 0
    while i < 500:
        i += 1
        if maximums is not None:
            if not dict_greater(maximums[1], total[1]):
                # dead end reached, return current total
                if debug: print 'dead end reached in greedy search algorithm'
                return currents
        if dict_greater(total[1], minimums[1]):
            if debug: print 'success, returning currents'
            return currents
        if len(possibilities) < 1:
            if debug: print 'out of new possibilities'
            return currents
        next_item = _next_item_helper(possibilities)
        currents.append(next_item)
        total[1] = dict_add(total[1], next_item[1])
    if debug: print 'end greedy_val'
    return currents


# Simple Indexers (smaller index value is better)
def finishline_indx(minimums, total, currents, maximums=None):
    """
    Measures total distance to the finish line of having all values in
    'currents' greater than or equal to those in 'minimums'
    optional: not used
    """
    distance = 0
    for key in minimums[1]:
        total_val, minimums_val = total[1][key], minimums[1][key]
        if total_val < minimums_val:
            if total_val is not None and minimums_val is not None:
                distance += ((minimums_val - total_val) / float(minimums_val))
    return distance

def balance_indx(minimums, total, currents, maximums=None):
    """
    Measures balance of currents, total distance to 'minimums' is calculated 
    and then the average distance is determined.  The distance of each value 
    of minimums to the average is then summed.
    """
    assert total[0] == 'total'
    assert type(total[1]) is dict
    assert minimums[0] == 'minimums'
    assert type(minimums[1]) is dict
    distance = 0 # total distance from perfect balance
    count = 0 # because we're finding an average
    for key in minimums[1].keys():
        #print 'minimums, total', minimums, total
        total_val, minimums_val = total[1][key], minimums[1][key]
        if total_val is not None and minimums_val is not None:
            distance += total_val / minimums_val ## is this right?
            count += 1
    average = distance/count
    b_factor = 0
    for key in minimums[1].keys():
        if total[1][key] is not None and minimums[1][key] is not None:
            ## this can be modified to weight foods that are behind
            b_factor += abs(average - (total[1][key] / minimums[1][key]))
    return b_factor

# Complex Indexers
def alternating_indx(minimums, total, currents, maximums=None):
    if len(currents) % 2 == 0:
        return finishline_indx(minimums, total, currents)
    else:
        return balance_indx(minimums, total, currents)

def runwalk_indx(minimums, total, currents, maximums=None):
    ## needs dict_sub method to find total - currents[-1]
    if len(currents) < 1:
        return finishline_indx(minimums, total, currents)
    last_total = ['total', dict_sub(total[1], currents[-1][1])]
    if finishline_indx(minimums, last_total, currents)/len(currents) < .75:
        return finishline_indx(minimums, total, currents)
    else:
        return balance_indx(minimums, total, currents)




## sanity tests
def test_greedy():
    minimums = ('minimums', {'a':10, 'b':100, 'c':12,  'd':17, 'e':5})
    maximums = ('maximums', {'a':57, 'b':145, 'c':99,  'd':82, 'e':123})
    possibilities = [('one', {'a':1, 'b':5, 'c':2,  'd':0, 'e':4}),
                     ('two', {'a':2, 'b':4, 'c':3,  'd':2, 'e':2}),
                     ('three', {'a':3, 'b':3, 'c':1,  'd':2, 'e':3}),
                     ('four', {'a':4, 'b':2, 'c':5,  'd':1, 'e':1}),
                     ('five', {'a':5, 'b':1, 'c':4,  'd':6, 'e':5}),
                     ]
    return ackp(possibilities, minimums, maximums, algorithm="greedy_balance")

def test_greedy_pickonce():
    minimums = ('minimums', {'a':10, 'b':100, 'c':12,  'd':17, 'e':5})
    maximums = ('maximums', {'a':87, 'b':145, 'c':99,  'd':82, 'e':123})
    possibilities = [('one', {'a':1, 'b':5, 'c':2,  'd':0, 'e':4}),
                     ('two', {'a':2, 'b':4, 'c':3,  'd':2, 'e':2}),
                     ('three', {'a':3, 'b':3, 'c':1,  'd':2, 'e':3}),
                     ('four', {'a':4, 'b':2, 'c':5,  'd':1, 'e':1}),
                     ('five', {'a':5, 'b':1, 'c':14,  'd':6, 'e':5}),
                     ('six', {'a':11, 'b':15, 'c':2,  'd':10, 'e':4}),
                     ('seven', {'a':12, 'b':14, 'c':3,  'd':2, 'e':2}),
                     ('eight', {'a':13, 'b':13, 'c':1,  'd':12, 'e':3}),
                     ('nine', {'a':14, 'b':22, 'c':15,  'd':1, 'e':1}),
                     ('ten', {'a':15, 'b':61, 'c':4,  'd':6, 'e':5}),
                     ]
    return ackp(possibilities, minimums, maximums, 
                algorithm="greedy_balance_pickonce")

def test_finishline_indx():
    minimums = ('minimums', {'a':30, 'b':100, 'c':12,  'd':18, 'e':50})
    half = ('total', {'a':15, 'b':50, 'c':6,  'd':9, 'e':25})
    full = ('total', {'a':30, 'b':100, 'c':12,  'd':18, 'e':50})
    tenth = ('total', {'a':3, 'b':10, 'c':1.2,  'd':1.8, 'e':5})
    print 'full', finishline_indx(minimums, full, None)
    print 'half', finishline_indx(minimums, half, None)
    print 'tenth', finishline_indx(minimums, tenth, None)

def test_greedy_finishline():
    minimums = ('minimums', {'a':10, 'b':100, 'c':12,  'd':17, 'e':5})
    maximums = ('maximums', {'a':87, 'b':145, 'c':99,  'd':82, 'e':123})
    possibilities = [('one', {'a':1, 'b':5, 'c':2,  'd':0, 'e':4}),
                     ('two', {'a':2, 'b':4, 'c':3,  'd':2, 'e':2}),
                     ('three', {'a':3, 'b':3, 'c':1,  'd':2, 'e':3}),
                     ('four', {'a':4, 'b':2, 'c':5,  'd':1, 'e':1}),
                     ('five', {'a':5, 'b':1, 'c':14,  'd':6, 'e':5}),
                     ('six', {'a':11, 'b':15, 'c':2,  'd':10, 'e':4}),
                     ('seven', {'a':12, 'b':14, 'c':3,  'd':2, 'e':2}),
                     ('eight', {'a':13, 'b':13, 'c':1,  'd':12, 'e':3}),
                     ('nine', {'a':14, 'b':22, 'c':15,  'd':1, 'e':1}),
                     ('ten', {'a':15, 'b':61, 'c':4,  'd':6, 'e':5}),
                     ]
    return ackp(possibilities, minimums, maximums, 
                algorithm="greedy_finishline")

def test_greedy_finishline_pickonce():
    minimums = ('minimums', {'a':10, 'b':100, 'c':12,  'd':17, 'e':5})
    maximums = ('maximums', {'a':87, 'b':145, 'c':99,  'd':82, 'e':123})
    possibilities = [('one', {'a':1, 'b':5, 'c':2,  'd':0, 'e':4}),
                     ('two', {'a':2, 'b':4, 'c':3,  'd':2, 'e':2}),
                     ('three', {'a':3, 'b':3, 'c':1,  'd':2, 'e':3}),
                     ('four', {'a':4, 'b':2, 'c':5,  'd':1, 'e':1}),
                     ('five', {'a':5, 'b':1, 'c':14,  'd':6, 'e':5}),
                     ('six', {'a':11, 'b':15, 'c':2,  'd':10, 'e':4}),
                     ('seven', {'a':12, 'b':14, 'c':3,  'd':2, 'e':2}),
                     ('eight', {'a':13, 'b':13, 'c':1,  'd':12, 'e':3}),
                     ('nine', {'a':14, 'b':22, 'c':15,  'd':1, 'e':1}),
                     ('ten', {'a':15, 'b':61, 'c':4,  'd':6, 'e':5}),
                     ]
    return ackp(possibilities, minimums, maximums, 
                algorithm="greedy_finishline_pickonce")


def test_greedy_alternating():
    minimums = ('minimums', {'a':10, 'b':100, 'c':12,  'd':17, 'e':5})
    maximums = ('maximums', {'a':87, 'b':145, 'c':99,  'd':82, 'e':123})
    possibilities = [('one', {'a':1, 'b':5, 'c':2,  'd':0, 'e':4}),
                     ('two', {'a':2, 'b':4, 'c':3,  'd':2, 'e':2}),
                     ('three', {'a':3, 'b':3, 'c':1,  'd':2, 'e':3}),
                     ('four', {'a':4, 'b':2, 'c':5,  'd':1, 'e':1}),
                     ('five', {'a':5, 'b':1, 'c':14,  'd':6, 'e':5}),
                     ('six', {'a':11, 'b':15, 'c':2,  'd':10, 'e':4}),
                     ('seven', {'a':12, 'b':14, 'c':3,  'd':2, 'e':2}),
                     ('eight', {'a':13, 'b':13, 'c':1,  'd':12, 'e':3}),
                     ('nine', {'a':14, 'b':22, 'c':15,  'd':1, 'e':1}),
                     ('ten', {'a':15, 'b':61, 'c':4,  'd':6, 'e':5}),
                     ]
    return ackp(possibilities, minimums, maximums, 
                algorithm="greedy_alternating")

def test_greedy_alternating_pickonce():
    minimums = ('minimums', {'a':10, 'b':100, 'c':12,  'd':17, 'e':5})
    maximums = ('maximums', {'a':87, 'b':145, 'c':99,  'd':82, 'e':123})
    possibilities = [('one', {'a':1, 'b':5, 'c':2,  'd':0, 'e':4}),
                     ('two', {'a':2, 'b':4, 'c':3,  'd':2, 'e':2}),
                     ('three', {'a':3, 'b':3, 'c':1,  'd':2, 'e':3}),
                     ('four', {'a':4, 'b':2, 'c':5,  'd':1, 'e':1}),
                     ('five', {'a':5, 'b':1, 'c':14,  'd':6, 'e':5}),
                     ('six', {'a':11, 'b':15, 'c':2,  'd':10, 'e':4}),
                     ('seven', {'a':12, 'b':14, 'c':3,  'd':2, 'e':2}),
                     ('eight', {'a':13, 'b':13, 'c':1,  'd':12, 'e':3}),
                     ('nine', {'a':14, 'b':22, 'c':15,  'd':1, 'e':1}),
                     ('ten', {'a':15, 'b':61, 'c':4,  'd':6, 'e':5}),
                     ]
    return ackp(possibilities, minimums, maximums, 
                algorithm="greedy_alternating_pickonce")

def test_greedy_runwalk():
    minimums = ('minimums', {'a':10, 'b':100, 'c':12,  'd':17, 'e':5})
    maximums = ('maximums', {'a':87, 'b':145, 'c':99,  'd':82, 'e':123})
    possibilities = [('one', {'a':1, 'b':5, 'c':2,  'd':0, 'e':4}),
                     ('two', {'a':2, 'b':4, 'c':3,  'd':2, 'e':2}),
                     ('three', {'a':3, 'b':3, 'c':1,  'd':2, 'e':3}),
                     ('four', {'a':4, 'b':2, 'c':5,  'd':1, 'e':1}),
                     ('five', {'a':5, 'b':1, 'c':14,  'd':6, 'e':5}),
                     ('six', {'a':11, 'b':15, 'c':2,  'd':10, 'e':4}),
                     ('seven', {'a':12, 'b':14, 'c':3,  'd':2, 'e':2}),
                     ('eight', {'a':13, 'b':13, 'c':1,  'd':12, 'e':3}),
                     ('nine', {'a':14, 'b':22, 'c':15,  'd':1, 'e':1}),
                     ('ten', {'a':15, 'b':61, 'c':4,  'd':6, 'e':5}),
                     ]
    return ackp(possibilities, minimums, maximums, 
                algorithm="greedy_runwalk")

def test_greedy_runwalk_pickonce():
    minimums = ('minimums', {'a':10, 'b':100, 'c':12,  'd':17, 'e':5})
    maximums = ('maximums', {'a':87, 'b':145, 'c':99,  'd':82, 'e':123})
    possibilities = [('one', {'a':1, 'b':5, 'c':2,  'd':0, 'e':4}),
                     ('two', {'a':2, 'b':4, 'c':3,  'd':2, 'e':2}),
                     ('three', {'a':3, 'b':3, 'c':1,  'd':2, 'e':3}),
                     ('four', {'a':4, 'b':2, 'c':5,  'd':1, 'e':1}),
                     ('five', {'a':5, 'b':1, 'c':14,  'd':6, 'e':5}),
                     ('six', {'a':11, 'b':15, 'c':2,  'd':10, 'e':4}),
                     ('seven', {'a':12, 'b':14, 'c':3,  'd':2, 'e':2}),
                     ('eight', {'a':13, 'b':13, 'c':1,  'd':12, 'e':3}),
                     ('nine', {'a':14, 'b':22, 'c':15,  'd':1, 'e':1}),
                     ('ten', {'a':15, 'b':61, 'c':4,  'd':6, 'e':5}),
                     ]
    return ackp(possibilities, minimums, maximums, 
                algorithm="greedy_runwalk_pickonce")
