import urllib.request
import requests
import re
# import pandas as pd
from bs4 import BeautifulSoup
from collections import OrderedDict

'''
Code will scrape UCM GE requirements website for the Social Science and Arts & Humanities GE courses.
Only the lower division courses will be retained.

The lower division GE classes from each department will be cross-referenced with lower division
courses found in the "Intellectual Experience Badges". Of interest are eight badges labeled:
    (1) 'Literary and Textual Analysis', (2) 'Media and Visual Analysis', 
    (3) 'Societies and Cultures of the Past', (4) 'Diversity and Identity', 
    (5) 'Global Awareness', (6) 'Sustainability', 
    (7) 'Ethics', (8) 'Leadership, Community, and Engaging the World'

The raw and cross-referenced data will be presented in an Excel spreadsheet for general use.
'''


##########  Scrape GE courses  ##########
# urllib kept returning an error, so used requests to retrieve html info
ge_html = requests.get(
    "https://catalog.ucmerced.edu/preview_program.php?catoid=17&poid=2135")
ge_soup = BeautifulSoup(ge_html.text, features="html.parser")


# Search for part of web page containing classes and convert them into a list of classes.
# Department information was not retrieved using href below. Dept. info was determined by
# alphabetical ordering of classes (eg., Social Sciences A-Z followed by Arts & Humanities A-Z).
ge_classes = ge_soup.find_all("a", href="#")
ge_classes_txt = [x.get_text() for x in ge_classes]


# clean the GE classes list by retaining only lower division courses using regular expressions.
# Some GE (and badged) courses contain values with anomalous characters such as "/a" and "\xa0".
# Must replace all values containing these characters with an empty string ("") or a string with
# a space (" "), respectively. Beware the following:
# "CCST 060: Introduction to Chicano/a Culture and Experiences",
# "ENG 032: Introduction to Chicano/a Culture and Experiences",
# "SPAN 060: Introduction to Chicano/a Culture and Experiences",
# "SPAN 050: Introduction to Hispanic\xa0Literatures"
regex = re.compile("[A-Z]{2,4}\s[0]{1}[0-9]{2}")
cleaned_ges = [x.replace("/a", "").replace("\xa0", " ")
               for x in ge_classes_txt if regex.match(x)]


# Create a dictionary where departments are keys and GE courses are values
# Do not like that this is hard coded according to index (used enumerate on cleaned_ges to determine indices)
# Will need to revisit this...

# for idx, itm in enumerate(cleaned_ges):
#    print(idx, itm)
ge_dict = {"Social Science Courses": cleaned_ges[:32],
           "Arts and Humanities Courses": cleaned_ges[32:]}
# print(ge_dict)


##########  Scrape Badged courses  ##########
# My function to scrape and retain list of lower division courses from the eight badges list
def scraped_badge_classes(some_url):
    '''
    Function opens and retrieves the contents of a URL to return a list of lower division courses
    satisfying "badge" requirements.

    Input: URL (of type string) containing list(s) of classes on UC website.
    Output: a cleaned list of only the lower division classes in eight "badge" requirements.
    '''

    # open and read url contents
    content = urllib.request.urlopen(some_url, data=None).read()
    soup = BeautifulSoup(content, features="html.parser")

    # search for section of web page containing classes and convert them into a list of classes.
    class_rows = soup.find("div", id="content-col2-1")
    rows = class_rows.get_text().split("\n")

    # further clean the classes list by keeping only lower division courses (classes numbered
    # between 000 to 099) using regular expressions.
    cleaned_rows = [row.strip("\t").replace(
        "/a", "").replace("\xa0", " ") for row in rows if ": " in row]
    regex = re.compile("[A-Z]{2,4}\s[0]{1}[0-9]{2}:")
    low_rows = [low for low in cleaned_rows if regex.match(low)]

    return low_rows


#####  Implement my function to obtain dictionary of badges (keys) and their lower division courses (values)  #####
badge_urls = [
    "https://ge.ucmerced.edu/intellectual-experience-badges/literary-and-textual-analysis",
    "https://ge.ucmerced.edu/intellectual-experience-badges/media-and-visual-analysis",
    "https://ge.ucmerced.edu/intellectual-experience-badges/societies-and-cultures-past",
    "https://ge.ucmerced.edu/intellectual-experience-badges/diversity-and-identity",
    "https://ge.ucmerced.edu/intellectual-experience-badges/global-awareness",
    "https://ge.ucmerced.edu/intellectual-experience-badges/sustainability",
    "https://ge.ucmerced.edu/intellectual-experience-badges/ethics",
    "https://ge.ucmerced.edu/intellectual-experience-badges/leadership-community-and-engaging-world"
]

badge_keys = [
    'Literary and Textual Analysis', 'Media and Visual Analysis', 'Societies and Cultures of the Past',
    'Diversity and Identity', 'Global Awareness', 'Sustainability', 'Ethics', 'Leadership, Community, and Engaging the World'
]


# Create a dictionary where badges are keys and badge-related courses are values using the scraped_badge_classes function
badges_dict = OrderedDict()
for i in range(len(badge_urls)):
    badges_dict[badge_keys[i]] = scraped_badge_classes(badge_urls[i])

# print(badges_dict)


#####  Cross-reference lower division classes in GEs with classes in badges  #####
# If GE class is found in ANY badges class lists, then append the class to the yes badges list via the xref_classes function.
# Otherwise, append the list to a no badges list.

def xref_classes(yes_lst_name, no_lst_name, GE_courses, badge_dict):
    '''
    Create a list of GE classes found in badged classes
    Input: 
        - yes_lst_name: to initiate an empty list to store courses found in badges list,
        - no_lst_name: to initiate an empty list to store courses not found in badges list,
        - GE_courses: a list of GE department lower division classes,
        - badge_dict: a dictionary of lower division courses found in eight badges
    Output: a tuple containing a list of GE classes found/not found in the badged classes;
          there may be duplicates in the "found" list, thus need to apply set() to eliminate duplicates
    '''
    yes_lst_name = []
    no_lst_name = []
    for itm in GE_courses:
        for i in badge_dict.keys():
            if itm in badge_dict[i]:
                yes_lst_name.append(itm)
        if itm not in yes_lst_name:
            no_lst_name.append(itm)

    return sorted(list(set(yes_lst_name))), no_lst_name


##### Implement my function to obtain list and (then dict below) of lower division GE courses found/not found in badges  #####
ss_yes_badges, ss_no_badges = xref_classes(
    "ss_yes", "ss_no", ge_dict["Social Science Courses"], badges_dict)
ah_yes_badges, ah_no_badges = xref_classes(
    "ah_yes", "ah_no", ge_dict["Arts and Humanities Courses"], badges_dict)


# Check/test to make sure sum of length of yes/no xreffed is equal to the length of the original lists
#print(len(ge_dict["Social Science Courses"]), len(ge_dict["Arts and Humanities Courses"]))


# Convert list of classes found/not found in badges into dictionary.
ge_badges_dict = {"Social Science in Badges": ss_yes_badges,
                  "Arts and Humanities in Badges": ah_yes_badges}
ge_no_badges_dict = {"Social Science not in Badges": ss_no_badges,
                     "Arts and Humanities not in Badges": ah_no_badges}
#print(ge_badges_dict, ge_no_badges_dict)

# print(ss_yes_badges)
# print(badges_dict[badge_keys[0]])


#####  One-hot encode lower division GE courses appearing in lower division Badged courses list   #####
# If GE class is found in a badge class lists, then append 1 to the output list, otherwise append 0.
def my_one_hot_encoding(GE_list, badges_list):
    '''
    Create a boolean list indicating whether the GE course appears in the badge course list. 
    1 indicates GE course is present. 0 indicates GE course is not present.

    Input: 
        - GE_list: a list of GE courses that appear in badges list at least once
        - badges_list: a list of courses from a single badge category
    Output:
        - a list of boolean values
    '''

    output = [1 if course in badges_list else 0 for course in GE_list]

    return output


##### Implement my function to obtain (boolean list and then) dict of lower division GE courses found various in badges  #####
# keys are GE title and values are boolean
ss_v_badges_dict = OrderedDict()
print('STEP 1: ')
print(ss_v_badges_dict)
print()

ss_v_badges_dict["Social Science Courses"] = ss_yes_badges[:]
print('STEP 2: ')
print(ss_v_badges_dict)
print()

for i in badge_keys:
    ss_v_badges_dict[i] = my_one_hot_encoding(ss_yes_badges, badges_dict[i])

print('STEP 3: ')
print(ss_v_badges_dict)
print()

ah_v_badges_dict = OrderedDict()
ah_v_badges_dict["Arts and Humanities Courses"] = ah_yes_badges[:]
for i in badge_keys:
    ah_v_badges_dict[i] = my_one_hot_encoding(ah_yes_badges, badges_dict[i])

# print('The FIRST ONE')
# print(ss_v_badges_dict)
# print()
# print('THE SECOND ONE')
# print(ah_v_badges_dict)


# Convert dictionaries into a pandas dataframe; each category contains different numbers of courses, so columns lengths
# will be different
# ge_df = pd.DataFrame.from_dict( { key:pd.Series(value) for key, value in ge_dict.items() } )
# badges_df = pd.DataFrame.from_dict( { key:pd.Series(value) for key, value in badges_dict.items() } )
# ge_yes_df = pd.DataFrame.from_dict( { key:pd.Series(value) for key, value in ge_badges_dict.items() } )
# ge_no_df = pd.DataFrame.from_dict( { key:pd.Series(value) for key, value in ge_no_badges_dict.items() } )
# ss_v_badges_df = pd.DataFrame.from_dict( { key:pd.Series(value) for key, value in ss_v_badges_dict.items() } )
# ah_v_badges_df = pd.DataFrame.from_dict( { key:pd.Series(value) for key, value in ah_v_badges_dict.items() } )

# print(ss_v_badges_df)
# print(ah_v_badges_df)


###  Save dataframe in an excel file  ###
# with pd.ExcelWriter("GE_analysis.xlsx") as writer:
#     ss_v_badges_df.to_excel(writer, sheet_name="LD SS v Badges")
#     ah_v_badges_df.to_excel(writer, sheet_name="LD AH v Badges")
#     ge_yes_df.to_excel(writer, sheet_name="LD GE in Badges")
#     ge_no_df.to_excel(writer, sheet_name="LD GE NOT IN Badges")
#     ge_df.to_excel(writer, sheet_name="LD GE Courses")
#     badges_df.to_excel(writer, sheet_name="LD Badge Courses")
