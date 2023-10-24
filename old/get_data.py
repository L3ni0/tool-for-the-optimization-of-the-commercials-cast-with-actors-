from pornhub_api import PornhubApi
from bs4 import BeautifulSoup
import requests
from http.cookiejar import MozillaCookieJar 
import re
from datetime import datetime
import os

str_today_date = str(datetime.today().strftime('%Y-%m-%d'))
today_filename = 'data/' + str_today_date +'_raw.csv'


def get_pornstar_list_generator():
    api = PornhubApi()
    pornstars = api.stars.all_detailed()

    unpacked_list = [*pornstars][0][1]
    for pornstars in unpacked_list:
        if not str(pornstars.star.star_thumb).startswith('https://ei.phncdn.com/pics/pornstars/default'):
            yield pornstars.star.star_name, pornstars.star.star_url, int(pornstars.star.videos_count_all)


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


if __name__ == '__main__':
    with open(today_filename,'w',encoding="utf-8") as file:

        file.write('star,date,video_count,views\n')

        for pornstar,url,count in get_pornstar_list_generator():
            try:
                file.write(f'{pornstar},{str_today_date},{count},{get_views(url)}\n')
            except:
                print(pornstar,url)
            