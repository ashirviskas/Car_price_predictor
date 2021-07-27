import sqlite3
import pandas as pd


def get_data():
    query = sqlite3.connect('autoplius_data.sqlite')
    make_model = pd.read_sql_query('SELECT DISTINCT make, model FROM scraped_data_final',
                                   query)
    make = pd.read_sql_query('SELECT DISTINCT make FROM scraped_data_final', query)['make']
    return make_model, make


def create_dict():
    selection = {}
    make_model, make = get_data()
    for each_make in make:
        model_dict = {}
        for index, row in make_model.iterrows():
            if row['make'] == str(each_make):
                a = row['model']
                model_dict[a] = [yr for yr in range(1990, 2021)]
        selection[each_make] = model_dict
    return selection


