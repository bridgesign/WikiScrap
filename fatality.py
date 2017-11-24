import requests
import re
import time
import datetime
import json
import operator
from bs4 import BeautifulSoup as BS

# This saves the table as a dictionary.
# The try statement will make sure that a failure in
# network adapters won't cause a problem and will retry


def table_content(link, year):
    try:
        with requests.get(link, stream=True) as req:
            bs = BS(req.text, 'html.parser')
    except:
        return(table_content(link))
    content = {}
    # Extracts info from all paragraphs
    paragraphs = bs.find_all('p')
    # Puts releavently long data as info
    for i in paragraphs:
        if len(i.text) > 100:
            content['info'] = i.text
            break
    # This will remove the reference links in the content.
    content['info'] = re.sub('\[\d+\]', '', content['info'])
    # This will look for all the tables with required information
    table = bs.find_all('table', class_='infobox vcard vevent')
    for i in table:
        tab_data = BS(str(i), 'html.parser').find_all("tr")
        for j in tab_data:
            if j.find('th', {'scope': 'row'}):
                content[j.th.text] = j.td.text
                # This will remove the reference links in the content.
                content[j.th.text] = re.sub('\[\d+\]', '', content[j.th.text])
    return([content, len(table), year])

# Function will put data in required format


def content(s):
    bs = BS(s, 'html.parser')

    content_list = bs.find_all('li')
    links = []
    for i in content_list:
        link = BS(str(i), 'html.parser')
        try:
            links.append('https://en.wikipedia.org'+link.a.get('href'))
        except:
            pass
    return([links, bs.h3.span.text])  # bs.h3.span.text Returns the year

try:
    file = open('temp.txt', 'r')
    print('Loading data...')
    all_data = json.loads(file.read())
    file.close()
except:
    ###
    # Note: This will take few hours. It will store the data in temp.txt.
    # Delete it to fetch a new copy of data
    ###

    print('Collecting data from wikipedia...')
    print("NOTE: This will take some time. This is required once to store the data.")
    print("      Delete temp.txt to make the program recollect the data (In case of updates on page)")
    print('Progress: <', end='')

    with requests.get('https://en.wikipedia.org/wiki/List_of_accidents_and_incidents_involving_commercial_aircraft', stream=True) as req:
        reg = '<h3>[^@]*?(?=<h3>|<h2>|<h1>)'
        accident_list = re.findall(reg, req.text)  # Stores the link data
    # Removes empty entries
    accident_list[:] = [j for j in accident_list if j != '']

    all_data = []
    for i in accident_list:
        con = content(i)
        for j in con[0]:
            # This produces a dictionary, the number of tables on the page and
            # the year of incident
            all_data.append(table_content(str(j), con[1]))
            time.sleep(0.5)
        print('=', end='')
    print('>')

    # Dumping The Data
    dump = json.dumps(all_data)
    file = open('temp.txt', 'w')
    file.write(dump)
    file.close()
    ##################

# This stores a list of dictionaries and adds a comparable fatality
# integer value with table lenght
fatality_l = []

# This takes the different flight origin and their incidents years
flight_origin = {}
# We need to check whether each key value exit for each table as data varies
# Also some tables have entries that others don't have
for i in all_data:
    if 'Flight origin' in i[0].keys():
        if i[0]['Flight origin'] in flight_origin.keys():
            flight_origin[i[0]['Flight origin']][0] += 1
        else:
            flight_origin[i[0]['Flight origin']] = [
                1, int(i[2])]                     # int(i[2]) is the year
    if 'Fatalities' in i[0].keys():
        # This line is for taking first numeric value
        fatality = re.search('\d+', i[0]['Fatalities'])
        if fatality != None:
            # Creates temporary copy for storing in required format
            temp_dict = i[0].copy()
            # Checks if date is there. If not places the date as year within ()
            if 'Date' not in temp_dict.keys():
                temp_dict['Date'] = '('+i[2]+')'
            temp_dict['fatality_value'] = int(fatality[0])
            temp_dict['table_num'] = i[1]
            fatality_l.append(temp_dict)

# Reverse sort the list according to key value
fatality_l.sort(key=operator.itemgetter('fatality_value'), reverse=True)

print()

print('To check the top n aviation incidents, input n below')

x = input('Number of incidents: ')

if x == '':
    x = 0
else:
    try:
        x = int(x)
    except:
        x = 0
        print('\nPlease put a valid positive integer')

print()
for i in range(x):
    # Checking whether info is available
    if 'info' in fatality_l[0]:
        print('Incident: '+fatality_l[0]['info']+'\n')
    print('Date: '+fatality_l[0]['Date']+'\n')
    print('Fatalities: '+fatality_l[0]['Fatalities']+'\n')
    # Checking whether Flight origin is available
    if 'Flight origin' in fatality_l[0]:
        print('Flight origin: '+fatality_l[0]['Flight origin']+'\n')
    else:
        print('Flight origin: No data')
    print()

    del fatality_l[0]
    if len(fatality_l) == 0:
        break

print('''To find the flight origin(whose data is available)
with maximum incidents in last y years, input y below''')

y = input('Look back in years: ')

if y == '':
    y = 0
else:
    try:
        y = int(y)
    except:
        y = 0
        print('\nPlease put a valid year')

# Gets the current year
current_year = int(datetime.datetime.now().year)

# Creates the list of all acceptable years
year_range = [j for j in range(current_year-y, current_year)]

# For storing the incident number for each flight origin
max_incident = []
for i in flight_origin.values():
    if i[1] in year_range:
        max_incident.append(i[0])

print('\n')

# Check for each case whether flight origin had maximum incidents
# Check for each case whether incident was in required year range

for i in flight_origin.keys():
    if ((len(max_incident) > 0)
            and (flight_origin[i][0] == max(max_incident))
            and (flight_origin[i][1] in year_range)
            and (i != 'n/a')):
        print(i, '\tIncidents:', flight_origin[i][0])
