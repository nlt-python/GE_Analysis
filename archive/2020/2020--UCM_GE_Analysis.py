import urllib.request
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
from collections import OrderedDict

'''
Code will scrape UCM GE requirements website for the Social Science and Arts & Humanities GE courses.
All lower division and upper division courses will be retained.

The GE classes from each department will be cross-referenced with courses found in the
"Intellectual Experience Badges". Of interest are 11 badges labeled:
    (1) 'Media and Visual Analysis',
    (2) 'Scientific Method',
    (3) 'Literary and Textual Analysis',
    (4) 'Quantitative and Numerical Analysis'
    (5) 'Societies and Cultures of the Past',
    (6) 'Diversity and Identity',
    (7) 'Global Awareness',
    (8) 'Sustainability',
    (9) 'Practical and Applied Knowledge'
    (10) 'Ethics',
    (11) 'Leadership, Community, and Engaging the World'

The raw and cross-referenced data will be presented in an Excel spreadsheet for general use.
'''

##########  Scrape GE courses  ##########
# urllib kept returning an error, so used requests to retrieve html info
ge_html = requests.get(
    " https://catalog.ucmerced.edu/preview_program.php?catoid=17&poid=2135")
ge_soup = BeautifulSoup(ge_html.text, features="html.parser")


# Search for part of web page containing classes and convert them into a list of classes.
# Department information was not retrieved using href below. Dept. info was determined by
# alphabetical ordering of classes (eg., Social Sciences A-Z followed by Arts & Humanities A-Z).
ge_classes = ge_soup.find_all("a", href="#")
ge_classes_txt = [x.get_text() for x in ge_classes]


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
ge_dict = {"Social Science Courses": cleaned_ges[:227],
           "Arts and Humanities Courses": cleaned_ges[227:]}
# print(ge_dict)


##########  Scrape Badged courses  ##########
# My function to scrape and retain list of lower and upper division courses from the 11 badges list


def scraped_badge_classes(some_url):
    """Function opens and retrieves the contents of a URL to return a list of lower
        and upper division courses satisfying "badge" requirements.

    Args:
        some_url (string): URL(of type string) containing list(s) of classes on UC website.

    Output:
        a cleaned list of the lower and upper division classes in eight "badge" requirements.
    """

    # open and read url contents
    content = urllib.request.urlopen(some_url, data=None).read()
    soup = BeautifulSoup(content, features="html.parser")

    # search for section of web page containing classes and convert them into a list of classes.
    class_rows = soup.find("div", id="content-col2-1")
    rows = class_rows.get_text().split("\n")

    # clean the classes list (keep lower and upper division courses) using regular expressions.
    cleaned_rows = [row.strip("\t").replace("/a", "").replace("\xa0", " ")
                    for row in rows if ": " in row]

    return cleaned_rows


#####  Implement my function to obtain dictionary of 11 badges (keys) and their courses (values)  #####
badge_urls = [
    "https://ge.ucmerced.edu/intellectual-experience-badges/media-and-visual-analysis",
    "https://ge.ucmerced.edu/intellectual-experience-badges/scientific-method",
    "https://ge.ucmerced.edu/intellectual-experience-badges/literary-and-textual-analysis",
    "https://ge.ucmerced.edu/intellectual-experience-badges/quantitative-and-numerical-analysis",
    "https://ge.ucmerced.edu/intellectual-experience-badges/societies-and-cultures-past",
    "https://ge.ucmerced.edu/intellectual-experience-badges/diversity-and-identity",
    "https://ge.ucmerced.edu/intellectual-experience-badges/global-awareness",
    "https://ge.ucmerced.edu/intellectual-experience-badges/sustainability",
    "https://ge.ucmerced.edu/intellectual-experience-badges/practical-and-applied-knowledge",
    "https://ge.ucmerced.edu/intellectual-experience-badges/ethics",
    "https://ge.ucmerced.edu/intellectual-experience-badges/leadership-community-and-engaging-world"
]

badge_keys = [
    'Media and Visual Analysis', 'Scientific Method', 'Literary and Textual Analysis',
    'Quantitative and Numerical Analysis', 'Societies and Cultures of the Past',
    'Diversity and Identity', 'Global Awareness', 'Sustainability', 'Practical and Applied Knowledge',
    'Ethics', 'Leadership, Community, and Engaging the World'
]


# Create a dictionary where badges are keys and badge-related courses are values using the scraped_badge_classes
# function
badges_dict = OrderedDict()
for i in range(len(badge_urls)):
    badges_dict[badge_keys[i]] = scraped_badge_classes(badge_urls[i])


#####  Cross-reference classes in GEs with classes in badges  #####
# If GE class is found in ANY badges class lists, then append the class to the yes badges list via the xref_classes
# function. Otherwise, append the list to a no badges list.


def xref_classes(GE_courses, badge_dict):
    """Create a list of GE classes that are also found in badged classes

    Args:
        yes_lst_name (list):
        no_lst_name (list): a list of GE classes NOT FOUND in badges list
        GE_courses (list): list of GE department classes
        badge_dict (dict): a dictionary courses found in 11 badges

    Output:
        a tuple containing a list of GE classes found/not found in the badged classes.

    """

    # initiate empty lists for GE classes found in badges list and
    # GE classes NOT FOUND in badges list
    yes_lst_name = []
    no_lst_name = []
    for itm in GE_courses:
        for i in badge_dict.keys():
            if itm in badge_dict[i]:
                yes_lst_name.append(itm)
        if itm not in yes_lst_name:
            no_lst_name.append(itm)

    # there may be duplicates in the "found" list, thus need to apply set() to eliminate duplicates
    return sorted(list(set(yes_lst_name))), no_lst_name


#####  Implement my function to obtain list and (then dict below) of lower and upper  #####
#####  division GE courses found/not found in badges  #####
ss_yes_badges, ss_no_badges = xref_classes(
    ge_dict["Social Science Courses"], badges_dict)
ah_yes_badges, ah_no_badges = xref_classes(
    ge_dict["Arts and Humanities Courses"], badges_dict)


# Convert list of classes found/not found in badges into dictionary.
ge_badges_dict = {"Social Science in Badges": ss_yes_badges,
                  "Arts and Humanities in Badges": ah_yes_badges}
ge_no_badges_dict = {"Social Science not in Badges": ss_no_badges,
                     "Arts and Humanities not in Badges": ah_no_badges}


#####  One-hot encode GE courses appearing in Badges courses list   #####
# If GE class is found in a badge class list, then append 1 to the output list, otherwise append 0.


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


'''
#####  Implement my function to obtain (boolean list and then) dict of lower division GE courses  #####
#####  found in various badges  #####
# keys are GE title and values are boolean
ss_v_badges_dict = OrderedDict()
ss_v_badges_dict["Social Science Courses"] = ss_yes_badges[:]
for i in badge_keys:
    ss_v_badges_dict[i] = my_one_hot_encoding(ss_yes_badges, badges_dict[i])

ah_v_badges_dict = OrderedDict()
ah_v_badges_dict["Arts and Humanities Courses"] = ah_yes_badges[:]
for i in badge_keys:
    ah_v_badges_dict[i] = my_one_hot_encoding(ah_yes_badges, badges_dict[i])


# Convert dictionaries into a pandas dataframe; each category contains different numbers of courses, so columns lengths
# will be different
ge_df = pd.DataFrame.from_dict({key: pd.Series(value)
                                for key, value in ge_dict.items()})
badges_df = pd.DataFrame.from_dict(
    {key: pd.Series(value) for key, value in badges_dict.items()})
ge_yes_df = pd.DataFrame.from_dict(
    {key: pd.Series(value) for key, value in ge_badges_dict.items()})
ge_no_df = pd.DataFrame.from_dict(
    {key: pd.Series(value) for key, value in ge_no_badges_dict.items()})
ss_v_badges_df = pd.DataFrame.from_dict(
    {key: pd.Series(value) for key, value in ss_v_badges_dict.items()})
ah_v_badges_df = pd.DataFrame.from_dict(
    {key: pd.Series(value) for key, value in ah_v_badges_dict.items()})
# print(ss_v_badges_df)
# print(ah_v_badges_df)


###  Save dataframe in an excel file  ###
with pd.ExcelWriter("GE_analysis.xlsx") as writer:
    ss_v_badges_df.to_excel(writer, sheet_name="LD SS v Badges")
    ah_v_badges_df.to_excel(writer, sheet_name="LD AH v Badges")
    ge_yes_df.to_excel(writer, sheet_name="LD GE in Badges")
    ge_no_df.to_excel(writer, sheet_name="LD GE NOT IN Badges")
    ge_df.to_excel(writer, sheet_name="LD GE Courses")
    badges_df.to_excel(writer, sheet_name="LD Badge Courses")
'''

if __name__ == "__main__":

    # print(ge_classes_txt)

    # for ges in cleaned_ges:
    #     print(ges)

    # for ss_ah, classes in ge_dict.items():
    #     print(f'{ss_ah}:  {classes}')
    #     print()

    # for badge, classes in badges_dict.items():
    #     print(badge)
    #     for c in classes:
    #         print(c)
    #     print()

    # Check to make sure sum of length of yes/no xreffed is equal to the length of the original lists
    # print('Check all GEs classes are distributed into Social Science and Arts & Humanties:  ')
    # print('    All GEs length: ', len(cleaned_ges))
    # print('    Social Sciences length: ', len(
    #     ge_dict["Social Science Courses"]))
    # print('    Arts & Humanities length: ', len(
    #     ge_dict["Arts and Humanities Courses"]))
    # print()

    # for ss_ah, classes in ge_badges_dict.items():
    #     print("GE Classes in Badges list: ", ss_ah, len(classes))
    #     print()

    # for ss_ah, classes in ge_no_badges_dict.items():
    #     print("GE Classes NOT IN Badges list: ", ss_ah, len(classes))
    #     print()

    # print(ge_badges_dict, ge_no_badges_dict)

    # print(ss_yes_badges)
    # print(badges_dict[badge_keys[0]])

    # print(ss_v_badges_dict)
    # print()
    # print(ah_v_badges_dict)
    # print()
