import pandas as pd
from bs4 import BeautifulSoup
from os import path, makedirs
import re

homedir = path.dirname(__file__)
df_archives = pd.read_csv(homedir + "/input/archives.csv", sep = ";")

def wrangler(html_file, design, year):
    with open(html_file, "r", encoding = "utf-8") as file:
        html_string = file.read()
    html_string = re.sub(r"\s*(?:\[|\()(the\s)?white album(?:\))?\s*(?:\])?", "", html_string)
    doc = BeautifulSoup(html_string, "html.parser")
    counter = 0
    result_dict = {}
    if design == 1:
        table = doc.find("table", {"width": "100%"})
        rows = table.find_all("tr")
        for row in rows:
            counter = int(row.text.split("\n")[0])
            row_split = row.text.strip().split(":")
            artist = re.sub(r"([0-9]+)", "", row_split[0]).strip("\n").strip()
            if year == 2001:
                album = row_split[1]
            else:
                #album = row_split[1][:-6].strip("\n").strip()
                album = re.sub(r"/\[.*\]", "", row_split[1])[:-6].strip("\n").strip()
            result_dict[counter] = [artist, album]
            if counter == 40:
                break
    elif design == 2:
        table = doc.find("table", {"id": "user_list"})
        rows = table.find_all("tr")
        for row in rows:
            counter = int(row.find("td", {"valign": "center"}).text)
            main_entry = row.find("td", {"class": "main_entry"})
            artist = main_entry.find("a", {"class": "list_artist"}).text
            album = re.sub(r"\s*\[[^\]]*\]\s*", "", main_entry.find("a", {"class": "list_album"}).text)
            result_dict[counter] = [artist, album]
            if counter == 40:
                break
    elif design == 3:
        table = doc.find("table", {"id": "user_list"})
        if year == 2009: 
            first_date = "august 06, 2009"
            second_date = "august 30, 2009"
        if year == 2010: 
            first_date = "may 05, 2010"
            second_date = "may 27, 2010"
        if year == 2011: 
            first_date = "may 10, 2011"
            second_date = "june 30, 2011"
        if year == 2012: 
            first_date = "april 04, 2012"
            second_date = "june 07, 2012"
        if year == 2013: 
            first_date = "may 01, 2013"
            second_date = "june 07, 2013"
        if year == 2016: 
            first_date = "may 02, 2016"
            second_date = "june 01, 2016"
        if year == 2017: 
            first_date = "may 01, 2017"
            second_date = "june 05, 2017"
        rows = table.text.split(first_date)[1].split(second_date)[0].split("\n")
        for row in rows:
            if row:
                counter += 1
                row = row.strip("(-)")
                row_split = row.split("-")
                artist = row_split[1].strip()
                #album = re.sub(r"\s*\(\d{4}\)", "", row_split[2]).strip()
                album_list = row_split[2].strip().split(" ")[:-1]
                album = " ".join(album_list)
                result_dict[counter] = [artist, album]
                if counter == 40:
                    break
    elif design == 4:
        table = doc.find("table", {"class": "mbgen"})
        rows = table.find_all("tr")
        for row in rows:
            if not "javascript" in str(row):
                counter = int(row.find("span", {"class": "ooookiig"}).text)
                artist = row.find("a", {"class": "artist"}).text
                album = row.find("a", {"class": "album"}).text
                result_dict[counter] = [artist, album]
                if counter == 40:
                    break
    elif design == 5:
        divs = doc.find_all("div", {"class": "topcharts_itembox chart_item_release"})
        for div in divs:
            counter = int(div.find("div", {"class": "topcharts_position"}).text.strip("."))
            artist = div.find("a", {"class": "artist"}).text
            album = div.find("a", {"class": "release"}).text
            result_dict[counter] = [artist, album]
            if counter == 40:
                break
    elif design == 6:
        divs = doc.find_all("div", {"class": "page_charts_section_charts_item object_release"})
        for div in divs:
            counter += 1
            artist = div.find("a", {"class": "artist"}).text.strip("\n")
            album = div.find("a", {"class": "page_charts_section_charts_item_link release"}).text.strip("\n")
            result_dict[counter] = [artist, album]
            if counter == 40:
                break
    df = pd.DataFrame.from_dict(result_dict, orient = "index").rename(columns = {0: str(year) + "_artist", 1: str(year) + "_album"})
    return df

df_list = []
for index, row in df_archives.iterrows():
    if str(row["link"]) != "nan":
        html_file = str(homedir + "/scraped/" + str(row["year"]) + ".txt")
        design = int(row["design"])
        year = int(row["year"])
        print(year)
        df = wrangler(html_file, design, year)
        df_list.append(df)
df_combined = pd.concat(df_list, axis = 1)
print(df_combined[:40])

if not path.exists(homedir + "/output"):
    makedirs(homedir + "/output")
df_combined.to_csv(homedir + "/output/top_albums_over_time.csv", sep = ";", index = False)