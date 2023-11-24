from pornhub_api import PornhubApi
from bs4 import BeautifulSoup
import requests
from http.cookiejar import MozillaCookieJar 
import re
from datetime import datetime
import os

str_today_date = str(datetime.today().strftime('%Y-%m-%d'))
today_filename = 'data/' + str_today_date +'_raw.csv'
s = requests.Session()
jar = MozillaCookieJar('cookies.txt')
jar.load()

def get_pornstar_dict():
    api = PornhubApi()
    pornstars = api.stars.all_detailed()

    unpacked_list = [*pornstars][0][1]
    # for pornstars in unpacked_list:
    #     if not str(pornstars.star.star_thumb).startswith('https://ei.phncdn.com/pics/pornstars/default'):
    #         yield pornstars.star.star_name, pornstars.star.star_url, int(pornstars.star.videos_count_all)
    return {pornstar.star.star_name : [int(pornstar.star.videos_count_all),pornstar.star.star_url]  for pornstar in unpacked_list}

def get_views(link):
    global s, jar
    print(link)
    r = requests.get(link, cookies=jar)
    soup = BeautifulSoup(r.text, 'html.parser')
    star_info = soup.find('div', class_='infoBox videoViews tooltipTrig') or soup.find('div', class_='tooltipTrig infoBox videoViews')

    if star_info:

        star_info = star_info.get('data-title')
        number = int(''.join(re.findall('\d',star_info)))
        return number
    else:
        return -1



if __name__ == '__main__':
    
    pornstar_video_count_dict = get_pornstar_dict()
    with open(today_filename,'w',encoding="utf-8") as file:

        file.write('star,date,video_count,views\n')

        with open('stars.csv','r',encoding="utf-8") as stars_links_file:
            stars_links_file.readline()


            for line in stars_links_file:
                pornstar,url = line.split(',')
                if pornstar in pornstar_video_count_dict:
                    url = pornstar_video_count_dict[pornstar][1]
                    try:

                        file.write(f'{pornstar},{str_today_date},{pornstar_video_count_dict[pornstar][0]},{get_views(url)}\n')
                    except:
                        print(pornstar,url)
                