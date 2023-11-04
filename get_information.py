from pornhub_api import PornhubApi
from bs4 import BeautifulSoup
import requests
from http.cookiejar import MozillaCookieJar 
import re
from datetime import date


filename = 'data/information/general_information.csv'
s = requests.Session()
jar = MozillaCookieJar('cookies.txt')
jar.load()
today_date = date.today()

def get_info(link):
    global s, jar

    r = requests.get(link, cookies=jar)
    soup = BeautifulSoup(r.text, 'html.parser')
    info_list = soup.find_all('div', class_='infoPiece')
    needed = ['Age','Birthplace:','Height:','Weight:','Gender:','Ethnicity:'] #
    informations = {}

    for line in info_list:

        html = str(line)
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div', class_='infoPiece')

        span_text = div.find('span').get_text()
        div_text = div.get_text().replace(':','')
        value = div_text.replace(span_text, '').strip()

        if span_text in ('Height:','Weight:'):

            value = value[value.find("(")+1:value.find(")")]
            value = int(''.join(re.findall('\d',value)))

        elif span_text == 'Born:':

            span_text = 'Age'
            value = value.split('\t')

            if len(value) > 1:
                value = value[-1]
            else:
                value = value[0].split('\n')[-1]

            value = today_date.year - date.fromisoformat(value).year

        else:
            value = value.split('\t')
            
            if len(value) > 1:
                value = value[-1]
            else:
                value = value[0].split('\n')[-1]
            
            if ',' in value:
                value = value.split(',')[-1].strip()

        informations[span_text] = value

    list_of_informations = [informations[i] if i in informations else None for i in needed]
    print(list_of_informations)
    return list_of_informations


def get_cost(link):
    global s, jar

    r = requests.get(link, cookies=jar)
    soup = BeautifulSoup(r.text, 'html.parser')
    star_info = soup.find('div', class_='infoBox videoViews tooltipTrig') or soup.find('div', class_='tooltipTrig infoBox videoViews')

    if star_info:

        return int(''.join(re.findall('\d',star_info.text)))/500
    else:
        return -1


if __name__ == '__main__':
    with open(filename,'w',encoding="utf-8") as file:

        file.write('star,Age,Birthplace,Height,Weight,Gender,Ethnicity,cost\n')

        with open('stars.csv','r',encoding="utf-8") as stars_links_file:
            stars_links_file.readline()

            for line in stars_links_file:

                pornstar,url = line.split(',')
                Age,Birthplace,Height,Weight,Gender,Ethnicity = get_info(url.strip())

                try:
                    if (cost:=get_cost(url.strip())) != -1:
                        file.write(f'{pornstar},{Age},{Birthplace},{Height},{Weight},{Gender},{Ethnicity},{cost}\n')
                except:
                    print(pornstar,url)