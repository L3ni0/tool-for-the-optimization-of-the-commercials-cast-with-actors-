from bs4 import BeautifulSoup
import requests
from http.cookiejar import MozillaCookieJar 
import re
from datetime import datetime
import os


def get_views(link):
    s = requests.Session()
    jar = MozillaCookieJar('cookies.txt')
    jar.load()
    r = requests.get(link, cookies=jar) 
    soup = BeautifulSoup(r.text, 'html.parser')
    star_info = soup.find('div', class_='infoBox videoViews tooltipTrig') or soup.find('div', class_='tooltipTrig infoBox videoViews')

    if star_info:
        return int(''.join(re.findall('\d',star_info.text)))
    else:
        return -1

# print(get_views('https://www.pornhub.com/pornstar/videos_overview?pornstar=aaliyah-jolie'))

today_filename = str(datetime.today().strftime('%Y-%m-%d'))+'.csv'

if os.path.exists(today_filename): # it checks if we something miss, only by numb of lines
    with open('stars.csv','r') as file:
        with open('data/'+today_filename,'r+') as result:

            for line in result:
                file.readline()

            for line in file:
                link = line.strip().split(',')[1]
                print(link)
                views = get_views(link)
                print(views)
                result.write(line.strip()+','+str(views)+'\n')
                


else:
    with open('stars.csv','r') as file:

        with open('data/'+today_filename,'w') as result:

            result.write(file.readline().strip()+",count"+'\n')

            for line in file:
                link = line.strip().split(',')[1]
                print(link)
                views = get_views(link)
                print(views)
                result.write(line.strip()+','+str(views)+'\n')

