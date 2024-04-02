"""
Script for Step 5:
Once you have done all of these in the notebook, create a Python script 
that can be called with a date (from a TikTok video). First, the script 
looks whether a CSV with cleaned articles is in our folder. 
If not, calls first the API function to get the articles and 
then the function that converts them into a CSV. 
Then, it loads the CSV into a dataframe and it uses filtering to get the articles 
for the desired date. These articles will be used for the Semantic Similarity 
portion of the TikTok Project.
"""

import os
import pandas as pd
import time
import requests
import json

myAPIkey = 'dAgeA3Jd143Ih1V0Nc7ljDmJwWyo7C6A'

# check if CSV for that date already exists
# if it does exist:
# - get that CSV
# if it does NOT exist:
# - makes that CSV
# loads the CSV into 


def getNYTArticles(year, month, apiKey):
    """Function that sends a request to the NYT API for all articles in a month
    and then stores the results in a JSON file.
    """
    # create URL
    URL = f"https://api.nytimes.com/svc/archive/v1/{year}/{month}.json?api-key={apiKey}"

    # send the request to get the data
    data = requests.get(URL)
    if data.status_code == 200:
        print("Successfully got the data.")

    dataJson = data.json() # get response as JSON

    with open(f"NYT_{year}-{month}.json", 'w') as fout:
        json.dump(dataJson, fout)

def flatten_article(article_dict):
    article_dict_flat = {}
    article_dict_flat['abstract'] = article_dict['abstract']
    article_dict_flat['lead_paragraph'] = article_dict['lead_paragraph']
    article_dict_flat['headline'] = article_dict['headline']['main']
    article_dict_flat['keywords'] = "; ".join(keyword['value'] for keyword in article_dict['keywords'] if isinstance(keyword['value'], str))
    article_dict_flat['pub_date'] = article_dict['pub_date'] # technically has date and time
    article_dict_flat['document_type'] = article_dict['document_type']
    article_dict_flat['section_name'] = article_dict['section_name']
    article_dict_flat['type_of_material'] = article_dict['type_of_material']
    return article_dict_flat

def daily_article_csv(date):
    """
    Many parts similar to daily_article_list()
    """
    cwd = os.getcwd()
    print(f"Searching for NYT articles from {date}")

    year = date[:4]
    month = date[5:7].strip('0')
    day = date[8:10]

    month_json_want = f"NYT_{year}-{month}.json"
    month_json_current = [file for file in os.listdir(cwd) if file.endswith(".json")] # check if that month's json is in the folder

    if month_json_want not in month_json_current: # if that month's json is not in the folder, get it
        print(f"Getting articles from {month}-{year}")
        getNYTArticles(year, month, myAPIkey)
    else:
        print(f"Already have articles from {month}-{year}")

    with open(os.path.join(cwd,month_json_want)) as inf:
        articles = json.load(inf)
    
    daily_article_dict_list = [flatten_article(article) for article in articles['response']['docs'] if article['pub_date'][:10] == date]
    daily_article_df = pd.DataFrame(daily_article_dict_list)

    daily_article_df.to_csv(f"NYT_{date}.csv")


def get_date_df(date):
    cwd = os.getcwd()

    daily_article_csv(date)
    date_df = pd.read_csv(os.path.join(cwd, f"NYT_{date}"))

    return date_df