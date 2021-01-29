'''
OBJECTIVE:

Create an Excel spreadsheet cross-referencing Social Sciences and Arts & Humanities courses
satisfying general education requirements with required courses listed in the school's
"Intellectual Experience Badges".


METHOD:

Scrape the UC Merced website for GE courses in the Social Sciences and Arts &
Humanities as well as the courses found in the 11 "Intellectual Experience
Badges" labeled:

    (1) 'Media and Visual Analysis',    (2) 'Scientific Method',
    (3) 'Literary and Textual Analysis',    (4) 'Quantitative and Numerical Analysis'
    (5) 'Societies and Cultures of the Past',    (6) 'Diversity and Identity',
    (7) 'Global Awareness',    (8) 'Sustainability',
    (9) 'Practical and Applied Knowledge'    (10) 'Ethics',
    (11) 'Leadership, Community, and Engaging the World'

and cross-reference the various sets of courses.
'''


import requests
from bs4 import BeautifulSoup
import pandas as pd


ge_url = 'https://catalog.ucmerced.edu/preview_program.php?catoid=17&poid=2135'
badge_url = 'https://ge.ucmerced.edu/intellectual-experience-badges'


def scrape_parse(an_url):
    """Scrape, parses website and returns a Beautiful Soup object

    Input: string. URL
    Output: BS4 object. A parsed Beautiful Soup object
    """

    courses = requests.get(an_url)
    soup = BeautifulSoup(courses.content, features='html.parser')

    return soup


def badge_links(an_url):
    """Scrapes and crawls website before parsing and returning a Beautiful Soup object

    Input: string. URL
    Output: list. A list of parsed Beautiful Soup objects
    """

    badges = requests.get(an_url)
    soup = BeautifulSoup(badges.content, features='html.parser')

    badge_links = []
    for item in soup.find_all('a'):
        if 'https://ge.ucmerced.edu/intellectual-experience-badges' in item.get('href'):
            badge_links.append(item.get('href'))

    soup_contents = []
    for link in badge_links:
        soup_contents.append(scrape_parse(link))

    return soup_contents


def extract_ges(ge_contents):
    """Create a dictionary of extracted text from parsed ge web contents where keys are
    the area of study and values are its respective classes

    Input: BS4 object
    Output: dict. A dictionary where keys are GE areas of study and values are GE classes
    """

    # Retrieves classes for all areas of study listed on the webpage
    courses = ge_contents.find_all("a", href="#")
    ges = [course.text for course in courses]

    # Remove all superfluous non-alphanumeric characters from class names such as
    # "/a" or "/as", but keep a record of those classes as a check.
    err_strs = []

    for idx, ele in enumerate(ges):
        if ("/as" in ele) or ("/a" in ele):
            err_strs.append(ele)
            ges[idx] = ele.replace("/as", "").replace("/a", "")

    # Split the classes according to their areas of study
    # By looking at the first letter of the class name, a break between the two areas
    # of study can be found since the classes in each area of study are listed in
    # alphabetical order.
    for idx in range(1, len(ges)):
        if ges[idx-1][0] > ges[idx][0]:
            split_at = idx

    # Retrieves headers for areas of study of classes
    areas = ge_contents.find_all("div", "acalog-core")
    study_area = [[x.text for x in ele][0] for ele in areas[:-1]]
    ge_classes = [ges[:split_at], ges[split_at:]]

    # Create a dictionary where keys are areas of study and values are list of
    # classes in the field.
    return dict(zip(study_area, ge_classes))


def extract_badges(badge_contents):
    """Create a dictionary of extracted text from parsed badge web contents where keys
    are the badge titles and values are its respective classes

    Input: list. A list of soup objects containing badge titles and badge classes
    Output: dict. A dictionary where keys are badge titles and values are badge classes
    """

    # Retrieves classes for all badges listed on the webpage
    all_classes = []
    for badge in badge_contents:
        contents = badge.find("div", id="content-col2-1")
        stripped_contents = []
        for course in contents.text.split('\n'):
            if ":" in course:
                stripped_contents.append(course)
        for idx, ele in enumerate(stripped_contents):
            if ("\xa0" in ele) or ("/as" in ele) or ("/a" in ele) or ("\t" in ele):
                stripped_contents[idx] = ele.replace("\xa0", "").replace(
                    "/as", "").replace("/a", "").replace("\t", "")

        all_classes.append(stripped_contents)

    # Retrieves headers for badge titles and courses
    badges = []
    for content in badge_contents:
        badges.append(content.find('h1', class_='title'))

    badge_titles = [title.text.strip()[7:] for title in badges]

    # Create a dictionary where keys are badge titles and values are list of
    # classes in the badge.
    return dict(zip(badge_titles, all_classes))


def stem(badges):
    """Create a dictionary where all badge classes are filtered for STEM general education
    classes.

    Input: dict. Dictionary containing badge titles and their classes
    Output: dict.
    """

    prefixes = ['BIO ', 'BIOE ', 'CHEM ', 'CSE ', 'ENGR ',
                'ENVE ', 'ESS ', 'MATH ', 'ME ', 'MSE ', 'PHYS ']

    flat_badges = sorted(
        list(set([course for badge in badges.values() for course in badge])))

    stem_courses = []
    for prefix in prefixes:
        for badge in flat_badges:
            if prefix in badge:
                stem_courses.append(badge)

    return {'Engineering Majors / 11 Intellectual Badges': stem_courses}


def in_or_not(ges, badges):
    """Create a two pandas dataframes of general education courses in or not in the
    badges list of courses.

    Input: two dicts. 2 dictionaries containing ge areas of study and their courses
        and badge titles and their classes
    Output: two pandas dataframes
    """

    # Flatten lists in badges:
    flat_badges = sorted(
        list(set([ele for sub_lst in badges.values() for ele in sub_lst])))

    yes_dict, no_dict = {}, {}
    for area, courses in ges.items():
        yes_lst, no_lst = [], []

        for ge in courses:
            if ge in flat_badges:
                yes_lst.append(ge)
            else:
                no_lst.append(ge)
        yes_dict[area] = sorted(list(set(yes_lst)))
        no_dict[area] = sorted(list(set(no_lst)))

    return yes_dict, no_dict


def xref(courses, badges):
    """Create a boolean dictionary to represent classes in an area of study that is present in
    a dictionary containing badges as keys and a list of their badge classes as values.

    Input:  list. List of classes
            dict. Dictionary containing badges as keys and lists of classes as values.
    Output: boolean dictionary
    """

    keys = [str(k) for k in courses]
    bool_dict = courses
    for badge in badges:
        for k in keys:
            bool_dict[badge] = [1 if val in badges[badge]
                                else 0 for val in courses[k]]

    return pd.DataFrame.from_dict({key: pd.Series(value) for key, value in bool_dict.items()})


def create_dfs(a_dict):
    """Create pandas DataFrames from dictionaries

    Input: dict
    Output: pandas dataframe
    """
    return pd.DataFrame.from_dict(
        {key: pd.Series(value) for key, value in a_dict.items()})


if __name__ == "__main__":

    # DF for GE CLASSES
    ge_soup = scrape_parse(ge_url)
    ge_classes = extract_ges(ge_soup)
    ges_df = create_dfs(ge_classes)
    # print(ges_df)

    # DF for BADGE CLASSES
    b_links = badge_links(badge_url)
    badge_classes = extract_badges(b_links)
    badges_df = create_dfs(badge_classes)
    # print(badges_df)

    # DF for IN, NOT IN BADGES
    in_dict, not_dict = in_or_not(ge_classes, badge_classes)
    in_df = create_dfs(in_dict)
    not_df = create_dfs(not_dict)
    # print(in_df)
    # print(not_df)

    # DF for XREFFING STEM and BADGES
    stem_dict = stem(badge_classes)
    stem_df = xref(stem_dict, badge_classes)
    # print(stem_df)

    # DF for XREFFING GEs and BADGES
    keys = [str(k)[:-8] for k in ge_classes]
    results = []
    for area, ge in ge_classes.items():
        results.append(xref({area: ge}, badge_classes))
    # print(results)

    # Export to Excel
    with pd.ExcelWriter("data/CrossReferenceGE-Badges.xlsx") as writer:

        for idx in range(len(keys)):
            results[idx].to_excel(writer, sheet_name=f'{keys[idx]} vs Badges')

        stem_df.to_excel(writer, sheet_name="STEM vs Badges")
        ges_df.to_excel(writer, sheet_name="GE Courses")
        badges_df.to_excel(writer, sheet_name="Badge Courses")
        in_df.to_excel(writer, sheet_name="In Badges")
        not_df.to_excel(writer, sheet_name="NOT In Badges")
