import os, random, sys, time
from selenium import webdriver
from bs4 import BeautifulSoup
import csv

#Creates browser, a new Chrome webdriver instance. Path specified to where Chrome driveris installed.
#Download Webdriver as outlined in the README text file

#replace with location of your Chrome driver
browser = webdriver.Chrome(executable_path="C:/Users/Kentaro Vadney's XPS/Desktop/Scrape Linkedin/Chrome Driver/chromedriver.exe")

#file points to file object created from calling open on config.txt
#replace with location of your config.txt file location
file = open("C:/Users/Kentaro Vadney's XPS/Desktop/Scrape filtered list of people/config.txt")

#lines points to the file called on my readlines
lines = file.readlines()

#saves username
username = lines[0]

#saves password
password = lines[1]

#saves link of filtered connection page
link = lines[2]

def login():
    """logs in the user into the linkedin account"""
    
    #the browser opens the given link
    browser.get('https://www.linkedin.com/uas/login')

    #finds the location of where to enter the username
    elementID = browser.find_element_by_id('username')

    #enters the username
    elementID.send_keys(username)

    #finds the location of where to enter the password
    elementID = browser.find_element_by_id('password')

    #enters the password
    elementID.send_keys(password)

    # This function call is commented out because it seems that linkedin automatically logs you in after the username and password is entered
    # clicks the 'login' button, i.e. submits the inputted info
    #elementID.submit()

def scroll():
    """scroll through page so that the entire page loads. This ensures all of the information is accessable."""
    SCROLL_PAUSE_TIME = 1

    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")

    for i in range(3):
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, (document.body.scrollHeight / 2));")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scrapeProfile():
    """scrapes a profile for :
    link, name, profile_title, location (loc), number of connections, company_name, job_title, join-date
    experience (exp),  college name, degree, major, and year
    """

    #loads the page source file into variable 'src'
    src = browser.page_source

    #converts src into a 'BeatifulSoup' object
    soup = BeautifulSoup(src, 'lxml')

    #find the div that contains name and location
    name_div = soup.find('div', {'class': 'flex-1 mr5'})

    #find the ul that contains the name and location
    name_loc = name_div.find_all('ul')

    #assign name to the name, and take out unnecessary formatting
    name = name_loc[0].find('li').get_text().strip()

    #assign loc to the location, and take out unnecessary foratting
    loc = name_loc[1].find('li').get_text().strip()

    #assign profile_title to the h2 header in name_div, get the text, and clear unnecessary formatting
    profile_title = name_div.find('h2').get_text().strip()

    #assign connection to the field where # of connections is contained
    connection = name_loc[1].find_all('li')

    #get the number of connections and take out unneeded formatting
    connection = connection[1].get_text().strip()

    #These lines add the information we gathered into the list, info
    info = []
    info.append(link)
    info.append(name)
    info.append(profile_title)
    info.append(loc)
    info.append(connection)

    """realized this is unnecessarry since the sub head line includes most recent job and company
    ###### EXPERIENCE SECTION #####

    exp_section = None here, which breaks my code when I set the link equal to my own linkedin account = "https://www.linkedin.com/in/kentarov/"
    #finds the experience section
    exp_section = soup.find('section', {'id': 'experience-section'})

    #dives into the specific locations where the information we want lies
    exp_section = exp_section.find('ul')
    li_tags = exp_section.find('div')
    a_tags = li_tags.find('a')

    #gets job title - doesn't worked for linked work experience
    job_title = a_tags.find('h3').get_text().strip()

    chained = False
    
    if 'Company Name' in job_title:
        titles = exp_section.find_all('div', {'class' : 'pv-entity__summary-info-v2 pv-entity__summary-info--background-section pv-entity__summary-info-margin-top'})
        job_title = titles[0].find('h3').get_text().strip()
        chained = True
    #gets company name
    if chained is False:
        company_name = a_tags.find_all('p')[1].get_text().strip()
    else:
        company_name = a_tags.find('h3').find_all('span')[1].get_text().strip()

    #gets experience
    try:
        exp = a_tags.find_all('h4')[1].find_all('span')[1].get_text().strip()
    except:
        exp = a_tags.find_all('h3')

    #appends info we just collected
    info.append(company_name)
    info.append(job_title)
    info.append(exp)

    """
    ##### EDUCATION #####

    #finds the section where info about education lies
    edu_section = soup.find('section', {'id': 'education-section'}).find('ul')

    #gets college name
    college_name = edu_section.find('h3').get_text().strip()

    #gets degree name
    degree_name = edu_section.find('p', {'class': 'pv-entity__secondary-title pv-entity__degree-name t-14 t-black t-normal'}).find_all('span')[1].get_text().strip()

    #gets the major
    major = edu_section.find('p', {'class': 'pv-entity__secondary-title pv-entity__fos t-14 t-black t-normal'}).find_all('span')[1].get_text().strip()

    #gets the years this person was in university
    degree_year = edu_section.find('p', {'class': 'pv-entity__dates t-14 t-black--light t-normal'}).find_all('span')[1].get_text().strip()

    #adds information we just collected to info
    info.append(college_name)
    info.append(degree_name)
    info.append(major)
    info.append(degree_year)

    writer.writerow(info)

def getNewProfileIDs(soup, profilesQueued):
    """
    This function searches through the filtered search section, and only opens the users that has not already been opened by this program.
    If the program is at the end of the page, the program clicks next and continues. set the maximum # of people you want to search with input MAX.
    """
    profilesID = []
    results = soup.find('ul', {'class' : 'search-results__list list-style-none' })
    all_links = results.find_all('a', {'data-control-name' : "search_srp_result"})
    for link in all_links:
        userID = link.get('href')
        if ((userID not in profilesQueued) and (userID not in visitedProfiles) and (userID not in profilesID)):
            profilesID.append(userID)
    return profilesID

#### CALL TO FUNCTIONS ###

visitedProfiles = []
profilesQueued = []

#replace with location of your input.csv file

CsvFile = open("C:/Users/Kentaro Vadney's XPS/Desktop/Scrape filtered list of people/input.csv", 'w', newline='')
# defining new variable passing two parameters
writer = csv.writer(CsvFile)

# writerow() method to the write to the file object
writer.writerow(["Link", "Full Name",	"Current Position",		"Location", 	"Number of Connections",	"Most recent education",	"Degree	Major",	"Years Studied"
])

login()

#browser goes to the link
browser.get(link)

scroll()

profilesQueued = getNewProfileIDs(BeautifulSoup(browser.page_source), profilesQueued)

while profilesQueued:
    visitingProfileID = profilesQueued.pop()
    visitedProfiles.append(visitingProfileID)
    fullLink = 'https://www.linkedin.com' + visitingProfileID
    browser.get(fullLink)
    scroll()
    scrapeProfile()

    # Add the ID to the visitedUsersFile
    #replace with location to your visitedUsersFile.csv location
    with open("C:/Users/Kentaro Vadney's XPS/Desktop/Scrape filtered list of people/VisitedUsers.csv", 'a') as visitedUsersFile:
        visitedUsersFile.write(str(visitingProfileID)+'\n')
    visitedUsersFile.close()
    
    time.sleep(random.uniform(5, 15))

print('congrats, you made it')

