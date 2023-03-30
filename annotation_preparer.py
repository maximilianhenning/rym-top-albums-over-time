import pandas as pd
from os import path, makedirs
from glob import glob
from bs4 import BeautifulSoup
import re
import requests

homedir = path.dirname(__file__)
df = pd.read_csv(homedir + "/output/top_albums_over_time.csv", sep = ";")

album_list = []
for column in df:
    if "album" in column:
        column_list = df[column].tolist()
        for album in column_list:
            if str(album) == "nan":
                print(column)
            else:
                album_list.append(str(album))
unique_album_list = sorted(list(set(album_list)))
df_new = pd.DataFrame(unique_album_list).rename(columns = {0: "album"})
df_new[["genres_top", "genres_secondary", "tags"]] = "tbd"

with open(homedir + "/scraped/2021.txt", "r", encoding = "utf-8") as file:
    genre_html_1 = file.read()
response = requests.get("https://web.archive.org/web/20201103020814/https://rateyourmusic.com/charts/top/album/all-time/2/#results")
genre_html_2 = response.text.lower()
genre_htmls = [genre_html_1, genre_html_2]
divs_list = []
for genre_html in genre_htmls:
    doc = BeautifulSoup(genre_html, "html.parser")
    divs = doc.find_all("div", {"class": "topcharts_itembox chart_item_release"})
    for div in divs:
        divs_list.append(div)
albums_dict = {}
for div in divs_list:
    if div.find("a", {"class": "release"}):
        album = div.find("a", {"class": "release"}).text.replace("\n", "")
    elif div.find("a", {"class": "release topcharts_item_title"}):
        album = div.find("a", {"class": "topcharts_item_title"}).text.replace("\n", "")
    genres_top = div.find("div", {"class": "topcharts_item_genres_container"}).text.replace("\n", "")
    if div.find("div", {"class": "topcharts_item_secondarygenres_container"}):
        genres_secondary = div.find("div", {"class": "topcharts_item_secondarygenres_container"}).text.replace("\n", "")
    else:
        genres_secondary = "nan"
    if div.find("div", {"class": "topcharts_item_descriptors_container"}):
        tags = div.find("div", {"class": "topcharts_item_descriptors_container"}).text.replace("\n", "")
    else:
        tags = "nan"
    albums_dict[album] = [genres_top, genres_secondary, tags]

folder_exists = False
albums_loaded = False
if path.exists(homedir + "/annotation"):
    folder_exists = True
    files = glob(homedir + "/annotation/*")
    for file in files:
        file_name = file.replace(homedir, "")
        if file_name == "/annotation\\albums_to_be_annotated.csv":
            albums_loaded = True
            df_albums_loaded = pd.read_csv(file, sep = ";")
if folder_exists and albums_loaded:
    df_loaded_details = df_albums_loaded.loc[df_albums_loaded["genres_top"] != "tbd"]
    df_loaded_no_details = df_albums_loaded.loc[df_albums_loaded["genres_top"] == "tbd"]
    albums_no_details = df_loaded_no_details["album"].tolist()
    albums_to_add_dict = {}
    albums_left_tbd = {}
    for album in albums_no_details:
        if album in albums_dict.keys():
            albums_to_add_dict[album] = albums_dict[album]
        else:
            albums_left_tbd[album] = ["tbd", "tbd", "tbd"]
    df_albums_to_add = pd.DataFrame.from_dict(albums_to_add_dict, orient = "index")
    df_albums_to_add = df_albums_to_add.reset_index().rename(columns = {"index": "album", 0: "genres_top", 1: "genres_secondary", 2: "tags"})
    df_albums_left_tbd = pd.DataFrame.from_dict(albums_left_tbd, orient = "index")
    df_albums_left_tbd = df_albums_left_tbd.reset_index().rename(columns = {"index": "album", 0: "genres_top", 1: "genres_secondary", 2: "tags"})
    df_albums = pd.concat([df_loaded_details, df_albums_to_add, df_albums_left_tbd])
    df_albums.to_csv(homedir + "/albums_to_be_annotated.csv", sep = ";", index = False)
else:
    if not folder_exists:
        makedirs(homedir + "/annotation")
    df_new.to_csv(homedir + "/annotation/albums_to_be_annotated.csv", sep = ";", index = False)
    # Complete this for good first run

genres_top_list = df_albums["genres_top"].tolist()
genres_secondary_list = df_albums["genres_secondary"].tolist()
genres_lists = genres_top_list + genres_secondary_list
genres = []
for genres_list in genres_lists:
    genres_list = str(genres_list)
    if ", " in genres_list:
        genres += [genre.strip() for genre in genres_list.split(", ")]
    else:
        genres.append(genres_list.strip())
genres = list(set(genres))
df_genres = pd.DataFrame(genres).rename(columns = {0: "genre"})
df_genres["parent1"] = "tbd"

genres_loaded = False
for file in files:
    file_name = file.replace(homedir, "")
    if file_name == "/annotation\\genres_to_be_annotated.csv":
        genres_loaded = True
        df_genres_loaded = pd.read_csv(file, sep = ";")
if genres_loaded:
    genres = df_genres_loaded["genre"].tolist()
    genres_new = df_genres["genre"].tolist()
    genres_to_add_dict = {}
    for genre in genres_new:
        if genre not in genres:
            genres_to_add_dict["genre"] = ["tbd"]
    df_genres_to_add = pd.DataFrame.from_dict(genres_to_add_dict, orient = "index")
    df_genres_to_add = df_genres_to_add.reset_index().rename(columns = {"index": "genre", 0: "parent1"})
    df_albums = pd.concat([df_genres_loaded, df_genres_to_add])
    df_albums.to_csv(homedir + "/annotation/genres_to_be_annotated.csv", sep = ";", index = False)
else:
    df_genres.to_csv(homedir + "/annotation/genres_to_be_annotated.csv", sep = ";", index = False)
    # Complete this for good first run