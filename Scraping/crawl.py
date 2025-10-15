from bs4 import BeautifulSoup
import requests
import json
import re
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}
page = requests.get("https://www.imdb.com/chart/top/?ref_=nv_mv_250",headers=headers).text

soup = BeautifulSoup(page,'html.parser')
script_tag = soup.find('script', type='application/ld+json')

json_data = json.loads(script_tag.string)
urls = [item['item']['url'] for item in json_data['itemListElement']]
print(len(urls))
list_of_dicts = []

for url in urls:
    mov1_dict = {}
    movie_page = requests.get(url,headers=headers).text
    soup = BeautifulSoup(movie_page,'html.parser')

    script_tag = soup.find('script', type='application/json')
    json_data = json.loads(script_tag.string)
    items = [item for item in json_data]

    movie_id = json_data["props"]["pageProps"]["tconst"]
    match = re.match(r'[a-zA-Z]+(\d+)', movie_id).group(1)
    mov1_dict["movie_id"] = match

    title = json_data["props"]["pageProps"]["aboveTheFoldData"]["originalTitleText"]["text"]
    mov1_dict["title"] = title

    year = json_data["props"]["pageProps"]["aboveTheFoldData"]["releaseYear"]["year"]
    mov1_dict["year"] = year

    if json_data["props"]["pageProps"]["aboveTheFoldData"]["certificate"] is not None:
        certificate = json_data["props"]["pageProps"]["aboveTheFoldData"]["certificate"]["rating"]
        mov1_dict["certificate"] = certificate
    else:
        mov1_dict["certificate"] = None

    runtime = json_data["props"]["pageProps"]["aboveTheFoldData"]["runtime"]["seconds"]
    mov1_dict["runtime"] = int(round(int(runtime)/60))
    
    genres = [item["node"]["primaryText"]["text"] for item in json_data["props"]["pageProps"]["aboveTheFoldData"]["interests"]["edges"]]
    mov1_dict["genres"] = genres

    for ite in json_data["props"]["pageProps"]["aboveTheFoldData"]["principalCredits"]:
        mov1_dict[ite["category"]["text"]] = [
            {"name": item["name"]["nameText"]["text"], "id": re.match(r'[a-zA-Z]+(\d+)', item["name"]["id"]).group(1)}
            for item in ite["credits"]
        ]
    if json_data["props"]["pageProps"]["mainColumnData"]["lifetimeGross"] is not None:
        gross_us_canada = json_data["props"]["pageProps"]["mainColumnData"]["lifetimeGross"]["total"]["amount"]
        mov1_dict["gross_us_canada"] = gross_us_canada
    else:
        mov1_dict["gross_us_canada"] = None

    print(mov1_dict)
    list_of_dicts.append(mov1_dict)


#print(len(list_of_dicts))
list_of_dicts_v2 = list_of_dicts.copy()

list_of_persons=[]
idx = 0
for dict in list_of_dicts_v2:
    mov_title = dict['title']
    mov_id = dict["movie_id"]
    print("***********")
    print(mov_title)
    print(dict)
    director = "Director"
    writers = "Writers"
    stars = "Stars"
    if "Director" in dict:
        director = "Director"
    else:
        director = "Directors"

    if "Writers" in dict:
        writers = "Writers"
    else:
        writers = "Writer"
    
    if "Stars" in dict:
        stars = "Stars"
    else:
        stars = "Star"

    if len(dict[director]) > 0:
        for dir in dict[director]:
            person_dict = {}
            idx += 1
            person_dict["role"] = "Director"
            person_dict["idx"] = idx
            person_dict["name"] = dir["name"]
            person_dict["id"] = dir["id"]
            person_dict["movie_title"] = mov_title
            person_dict["movie_id"] = mov_id
            list_of_persons.append(person_dict)
    else:
        person_dict = {}
        idx += 1
        person_dict["role"] = "Director"
        person_dict["idx"] = idx
        person_dict["name"] = None
        person_dict["id"] = None
        person_dict["movie_title"] = mov_title
        person_dict["movie_id"] = mov_id
        print('*************')
        print(mov_title)
        list_of_persons.append(person_dict)

    if len(dict[writers]) > 0:
        for wri in dict[writers]:
            person_dict = {}
            idx += 1
            person_dict["role"] = "Writer"
            person_dict["idx"] = idx
            person_dict["name"] = wri["name"]
            person_dict["id"] = wri["id"]
            person_dict["movie_title"] = mov_title
            person_dict["movie_id"] = mov_id
            list_of_persons.append(person_dict)
    else:
        person_dict = {}
        idx += 1
        person_dict["role"] = "Writer"
        person_dict["idx"] = idx
        person_dict["name"] = None
        person_dict["id"] = None
        person_dict["movie_title"] = mov_title
        person_dict["movie_id"] = mov_id
        print('*************')
        print(mov_title)
        list_of_persons.append(person_dict)

    if len(dict[stars]) > 0:
        for star in dict[stars]:
            person_dict = {}
            idx += 1
            person_dict["role"] = "Star"
            person_dict["idx"] = idx
            person_dict["name"] = star["name"]
            person_dict["id"] = star["id"]
            person_dict["movie_title"] = mov_title
            person_dict["movie_id"] = mov_id
            list_of_persons.append(person_dict)
    else:
        person_dict = {}
        idx += 1
        person_dict["role"] = "Star"
        person_dict["idx"] = idx
        person_dict["name"] = None
        person_dict["id"] = None
        person_dict["movie_title"] = mov_title
        person_dict["movie_id"] = mov_id
        print('*************')
        print(mov_title)
        list_of_persons.append(person_dict)


#print(list_of_persons)
idx = 0
for dict in list_of_dicts_v2:
    if "Director" in dict:
        director = "Director"
    else:
        director = "Directors"

    if "Writers" in dict:
        writers = "Writers"
    else:
        writers = "Writer"
    
    if "Stars" in dict:
        stars = "Stars"
    else:
        stars = "Star"
    idx += 1
    dict["idx"] = idx
    del dict[director]
    del dict[writers]
    del dict[stars]

print()
print("v2 list")
#print()
#print(list_of_dicts_v2)

normalized_genre_rows = []
for movie in list_of_dicts_v2:
    base_row = {
        'movie_id': movie['movie_id'],
        'title': movie['title'],
        'year': movie['year'],
        'certificate': movie['certificate'],
        'runtime': movie['runtime'],
        'gross_us_canada': movie['gross_us_canada'],
        'idx': movie['idx']
    }
    for genre in movie['genres']:
        row = base_row.copy()
        row['genre'] = genre
        normalized_genre_rows.append(row)

#print(len(normalized_genre_rows))

#print(len(list_of_persons))

df1 = pd.DataFrame(normalized_genre_rows)
df2 = pd.DataFrame(list_of_persons)

columns1 = ['movie_id', 'title', 'year', 'certificate', 'runtime', 'genre', 'gross_us_canada', 'idx']
df1 = df1[columns1]

columns2 = ['idx', 'id', 'name', 'role', 'movie_title', 'movie_id']
df2 = df2[columns2]
 
df1.to_csv('normalized_genre_rows.csv', index=False)
df2.to_csv('list_of_persons.csv', index=False)
