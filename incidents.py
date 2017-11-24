import requests
import re
from bs4 import BeautifulSoup as BS


# Function will put data in required format
def content(s, y):
    bs = BS(s, 'html.parser')
    # Check year
    if bs.h3.span.text != y:
        return False
    content_list = bs.find_all('li')
    links = []
    for i in content_list:
        link = BS(str(i), 'html.parser')
        try:
            links.append('link: https://en.wikipedia.org' +
                         link.a.get('href'))  # Storing the links
        except:
            links.append('link: No link found')
    return(content_list, links)  # Returning content and links respectively

reg = '<h3>[^@]*?(?=<h3>|<h2>|<h1>)'

with requests.get('https://en.wikipedia.org/wiki/List_of_accidents_and_incidents_involving_commercial_aircraft') as req:
    accident_list = re.findall(reg, req.text)  # Storing all yearwise data
# Removing empty entries
accident_list[:] = [j for j in accident_list if j != '']

y = ''
print('Input quit to quit')
while True:
    y = input('Enter the year: ').strip().lower()
    if y == 'quit':
        break

    for i in accident_list:
        output = content(i, y)
        if output != False:
            break
    print()
    # Defined to get number of subentries
    l = 0
    if output != False:
        for i in range(len(output[0])):
            # Check if subentries are there
            if not output[0][i].find('li') and l == 0:
                # Adds the year manually to the text
                print(y+' '+output[0][i].text)
            elif not output[0][i].find('li'):         # Puts the subentries
                print('\t'+output[0][i].text+'\n')
                l += (-1)
            else:
                # Defining the number entries
                l += len(output[0][i].find_all('li'))
                # Prints out the text part in the tag
                print(output[0][i].a.text)
            print()
            if output[1][i] != 'link: No link found':
                print(output[1][i]+'\n\n')
    else:
        print('No Data Found.\n')
