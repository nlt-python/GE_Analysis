import urllib.request
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
from collections import OrderedDict

'''
Code will scrape 11 UCM Intellectual Badge requirements websites where only STEM-based classes
with the prefix: BIO, BIOE, CHEM, CSS, ENGR, ENVE, ESS, MATH, ME, MSE, PHYS

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


#####  Filter Intellectual Badges for STEM classes  #####
# Filter for course numbers beginning with:
stem_courses = ['BIO ', 'BIOE', 'CHEM', 'CSE', 'ENGR',
                'ENVE', 'ESS', 'MATH', "ME", 'MSE', 'PHYS']


def stem_classes(badge_courses, stem_courses):
    """Create a list of STEM classes

    Args:
        badge (list): a list of courses found in an intellectual badge.

    Output:
        a list of STEM classes.

    """

    # initiate empty list for STEM classes
    stem = []
    for course in badge_courses:
        for x in stem_courses:
            if x in course:
                stem.append(course)

    return stem


#####  Implement my function to obtain list of STEM classes and then dict where  #####
#####  keys are badges and values are STEM classes  #####
stem_dict = OrderedDict()
for badge in badge_keys:
    stem_dict[badge] = stem_classes(badges_dict[badge], stem_courses)


#####  One-hot encode STEM courses appearing in Badges  #####
# Will need to first compile entire list of STEM classes

all_STEM = []
for badge, courses in stem_dict.items():
    for course in courses:
        if course not in all_STEM:
            all_STEM.append(course)

sorted_STEM = sorted(all_STEM)


def my_one_hot_encoding(all_STEM, badges_list):
    """Create a boolean list indicating whether the STEM course appears in the badge course list.
    1 indicates STEM course is present. 0 indicates STEM course is not present.

    Args:
        all_STEM (list): a list of all of the STEM courses in badges
        badges_list (list): a list of courses from a single badge category

    Returns:
        list: a list of boolean values
    """

    output = [1 if course in badges_list else 0 for course in all_STEM]

    return output


#####  Implement my function to obtain (boolean list and then) dict of STEM courses  #####
#####  found in various badges  #####
# keys are STEM course numbers and values are boolean

ohe_STEM = OrderedDict()
ohe_STEM['Engineering Majors/ 11 Intellectual Badges'] = sorted_STEM[:]

for badge_keys in stem_dict:
    ohe_STEM[badge_keys] = my_one_hot_encoding(
        sorted_STEM, stem_dict[badge_keys])


# Convert dictionary into a pandas dataframe
stem_df = pd.DataFrame.from_dict({key: pd.Series(value)
                                  for key, value in ohe_STEM.items()})


###  Save dataframe into an excel file  ###
with pd.ExcelWriter("2020--STEM_and_Badges.xlsx") as writer:
    stem_df.to_excel(writer, sheet_name="STEM courses")


if __name__ == "__main__":

    # for badge, courses in badges_dict.items():
    #     print(badge)
    #     for course in courses:
    #         print(course)
    #     print()

    count = 0
    for stem in all_STEM:
        if stem in badges_dict['Practical and Applied Knowledge']:
            count += 1
            print(f'{count}:   {stem}')

    for course in badges_dict['Practical and Applied Knowledge']:
        print(course)

    # # print(stem_dict['Scientific Method'])

    # print('Total number of STEM courses from 11 Intellectual Badges:')
    # print(len(all_STEM))
    # print()

    # for k, v in stem_dict.items():
    #     print(f'The {k} Intellectual badge has {len(v)} STEM courses in it')
    #     print(v)
    #     print()
