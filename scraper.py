from os import path
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time

homedir = path.dirname(__file__)
df_archives = pd.read_csv(homedir + "/input/archives.csv", sep = ";")

def archive_scraper(year, link):
    if str(link) == "nan":
        return
    print(year)
    response = requests.get(link)
    html_string = response.text
    #doc = BeautifulSoup(html_string, "html.parser")
    with open(homedir + "/scraped/" + str(year) + ".txt", "w", encoding = "utf-8") as file:
        file.write(html_string.lower())
    time.sleep(5)

for index, row in df_archives.iterrows():
    archive_scraper(row["year"], row["link"])
