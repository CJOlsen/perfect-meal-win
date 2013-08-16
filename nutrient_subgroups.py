nutrient_subgroups = {'Elements': set(['Sodium, Na', 'Phosphorus, P',
                                       'Manganese, Mn', 'Iron, Fe',
                                       'Potassium, K', 'Fluoride, F',
                                       'Selenium, Se', 'Magnesium, Mg',
                                       'Zinc, Zn', 'Copper, Cu', 'Calcium, Ca']),
                      'Vitamins': set(['Niacin', 'Menaquinone-4', 'Thiamin',
                                       'Folate, food', 'Vitamin B-6',
                                       'Tocopherol, gamma', 'Carotene, beta',
                                       'Pantothenic acid', 'Vitamin E, added',
                                       'Tocopherol, beta',
                                       'Vitamin C, total ascorbic acid',
                                       'Tocopherol, delta',
                                       'Cryptoxanthin, beta',
                                       'Vitamin D3 (cholecalciferol)',
                                       'Lycopene', 'Vitamin B-12, added',
                                       'Vitamin A, IU', 'Retinol',
                                       'Vitamin A, RAE', 'Dihydrophylloquinone',
                                       'Vitamin E (alpha-tocopherol)',
                                       'Lutein + zeaxanthin', 'Betaine',
                                       'Riboflavin', 'Vitamin D',
                                       'Vitamin D2 (ergocalciferol)',
                                       'Carotene, alpha', 'Folic acid',
                                       'Folate, total', 'Vitamin B-12',
                                       'Choline, total',
                                       'Vitamin K (phylloquinone)',
                                       'Vitamin D (D2 + D3)', 'Folate, DFE']),
                      'Energy': set(['Energy']),
                      'Sugars': set(['Galactose', 'Starch', 'Lactose', 'Sucrose',
                                     'Maltose', 'Fructose', 'Glucose (dextrose)']),
                      'Amino Acids': set(['Lysine', 'Alanine', 'Glycine',
                                          'Proline', 'Serine', 'Arginine',
                                          'Glutamic acid', 'Phenylalanine',
                                          'Leucine', 'Methionine', 'Histidine',
                                          'Valine', 'Tryptophan', 'Isoleucine',
                                          'Threonine', 'Aspartic acid',
                                          'Cystine', 'Tyrosine']),
                      'Other': set(['Alcohol, ethyl', 'Ash', 'Beta-sitosterol',
                                    'Stigmasterol',
                                    'Fatty acids, total trans-monoenoic',
                                    'Theobromine', 'Caffeine',
                                    'Fatty acids, total trans',
                                    'Fatty acids, total trans-polyenoic',
                                    'Fatty acids, total polyunsaturated',
                                    'Fatty acids, total saturated',
                                    'Campesterol', 'Cholesterol',
                                    'Fatty acids, total monounsaturated',
                                    'Phytosterols']),
                      'Composition': set(['Fiber, total dietary',
                                          'Adjusted Protein', 'Water',
                                          'Total lipid (fat)', 'Protein',
                                          'Carbohydrate, by difference',
                                          'Sugars, total'])}


#IU_conversions:::: 'Vitamin A':  0.3 mcg retinol, 0.6 mcg beta-carotene

## these are max/min values from the USDA (find link, put it here)
## all values in mg !!!!
## http://www.iom.edu/Global/News%20Announcements/~/media/Files/Activity%20Files/Nutrition/DRIs/DRI_Summary_Listing.pdf
## http://iom.edu/Activities/Nutrition/SummaryDRIs/~~/media/Files/Activity%20Files/Nutrition/DRIs/RDA%20and%20AIs_Vitamin%20and%20Elements.pdf
#
## ******** (are some of these actually in GRAMS????????) ********
##daily_min_content = Nutrients(vitamin_a=.9, vitamin_c=90., vitamin_d=.015,
##                              vitamin_e=15., vitamin_k=.12, thiamin=1.2,
##                              riboflavin=1.3, niacin=16., vitamin_b6=0,
##                              folate=.4, vitamin_b12=.0024, pantothenic_acid=5.,
##                              biotin=30., choline=550., calcium=1000.,
##                              chromium=.035, copper=.9, fluoride=4.,
##                              iodine=.15, iron=8., magnesium=420.,
##                              manganese=2.3, molybdenum=.045, phosphorus=700.,
##                              selenium=.055, zinc=11., potassium=4700.,
##                              sodium=1500., chloride=2300.)
##
##daily_max_content = Nutrients(vitamin_a=3., vitamin_c=2000., vitamin_d=.05,
##                              vitamin_e=1000., vitamin_k=999999, thiamin=999999,
##                              riboflavin=999999, niacin=35., vitamin_b6=100,
##                              folate=1., vitamin_b12=999999, pantothenic_acid=999999,
##                              biotin=999999, choline=3500., calcium=2500.,
##                              chromium=999999, copper=10., fluoride=10,
##                              iodine=1.1, iron=45., magnesium=999999,
##                              manganese=11., molybdenum=2., phosphorus=4000.,
##                              selenium=.4, zinc=40., potassium=999999,
##                              sodium=2300., chloride=3600.)


## Vitamin A IU --> mg  (1000 IU == 300 mcg == .3 mg, 1 IU = 3/10,000 mg)
## the considerations of various Vitamin A measurements is beyond me...
## vitamin E is broken up between 'added' and 'alpha-tocopherol' (why?)
## is Iodine not in the database?  (that can't be...)
## Biotin not in the database?
#
