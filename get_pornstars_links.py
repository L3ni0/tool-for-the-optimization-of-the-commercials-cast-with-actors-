from pornhub_api import PornhubApi


def get_pornstar_list():
    api = PornhubApi()
    pornstars = api.stars.all_detailed()

    unpacked_list = [*pornstars][0][1]
    for pornstars in unpacked_list:
        if not str(pornstars.star.star_thumb).startswith('https://ei.phncdn.com/pics/pornstars/default') and int(pornstars.star.videos_count_all) > 30:
            yield pornstars.star.star_name, pornstars.star.star_url

with open('stars.csv','w',encoding="utf-8") as file:
    file.write('star,url\n')
    for pornstar,url in get_pornstar_list():
        try:
            file.write(f'{pornstar},{url}\n')
        except:
            print(pornstar,url)
            