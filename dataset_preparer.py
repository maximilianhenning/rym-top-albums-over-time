from os import path
import pandas as pd
import re

# Genres

homedir = path.dirname(__file__)
df_genres = pd.read_csv(homedir + "/annotation/genres_to_be_annotated.csv", sep = ";")

df_parent2 = df_genres.loc[df_genres["parent1"].notna()]
def parent_finder(genre):
    parent = str(df_genres.loc[df_genres["genre"] == genre]["parent1"].values)
    parent = re.sub(r"[\[\]']", "", parent)
    return parent
df_parent2["parent2"] = df_parent2["parent1"].apply(parent_finder)
df_parent3 = df_parent2.loc[df_parent2["parent2"].notna()]
df_parent3["parent3"] = df_parent3["parent2"].apply(parent_finder)

df_genres_combined = df_genres[["genre", "parent1"]]
df_genres_combined["parent2"] = df_parent2["parent2"]
df_genres_combined["parent3"] = df_parent3["parent3"]

df_genres_combined.to_csv(homedir + "/output/genres.csv", sep = ";")

# Albums

df_albums = pd.read_csv(homedir + "/annotation/albums_to_be_annotated.csv", sep = ";")

def album_cleaner(input):
    input = str(input).lower()
    input = input.replace(", ", ",")
    return input
df_albums["genres_top"] = df_albums["genres_top"].apply(album_cleaner)
df_albums["genres_secondary"] = df_albums["genres_secondary"].apply(album_cleaner)
df_albums["tags"] = df_albums["tags"].apply(album_cleaner)

df_albums.to_csv(homedir + "/output/albums.csv", sep = ";", index = False)

# Top albums