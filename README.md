# GE_Analysis
Scrapes and analyzes GE course requirements

At UC Merced, undergraduate students must complete classes affiliated with a set of 11 Intellectual badges along with their general education requirements in order to graduate. The classes associated with these 11 badges are spread across 11 different websites and the classes associated with the general education requirements are also located at yet other websites. This makes it a non-trivial task for student counselors to keep track of and best advise their students.
&nbsp;  

In this project, I will retrieve general education courses from UC Merced's Social Sciences and Arts & Humanities website and compile them into a spreadsheet. I will also scrape links to the 11 different badge websites and retrieve their respective courses from these links and compile them into a spreadsheet.
&nbsp;  

Additionally, I will also create spreadsheets that will cross-reference the general education courses that overlap with the courses associated with the Intellectual badges.

 - The complete source code to create an Excel workbook with multiple worksheets is located in the file /src/scrape.py.
 - A sort-of-tutorial to create pandas dataframes of the items listed is located in the Jupyter Notebook file notebook.ipynb.
 - The resulting workbook is located in the file /data/CrossReferenceGE-Badges.xlsx
