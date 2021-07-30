import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle
from time import perf_counter


class AutopliusPredictor:
    """
    Sukuriamas ML modelis naudojant visus 24k skelbimus iš Autoplius trauktus 2021.07.13.
    Naudojami kriterijai markė, modelis, metai, rida, transmisija, kėbulo tipas ir kuras.
    """
    def __init__(self):
        self.final_df = None
        self.model = None
        self.score = None
        self.create_dataframe()

    def connect_to_db(self):
        """
        jungimasis prie DB
        :return:
        """
        con = sqlite3.connect("autoplius_data.sqlite")
        return con

    def create_dataframe(self):
        """
        suformuojamas DataFrame objektas tinkamas modelio apmokymui. Ištraukiami visi
        skelbimai iš DB, sukuriami dummies, pašalinama string tipo data.
        data,
        pašalinami
        :return: DataFrame objektas
        """
        con = self.connect_to_db()
        df = pd.read_sql_query("SELECT * FROM scraped_data_final", con)
        dummies_make = pd.get_dummies(df['make'])
        dummies_model = pd.get_dummies(df['model'])
        dummies_tran = pd.get_dummies(df['tran'])
        dummies_type = pd.get_dummies(df['type'])
        dummies_fuel = pd.get_dummies(df['fuel'])
        self.final_df = pd.concat([df, dummies_make, dummies_model, dummies_type, dummies_tran, dummies_fuel], axis=1)
        self.final_df.drop(['id', 'make', 'model', 'type', 'tran', 'fuel'], axis=1, inplace=True)
        price = self.final_df.pop('price')
        self.final_df.insert(0, 'price', price)
        return self.final_df

    def load_model_data(self):
        """
        iš DataFrame objekto atskiria X ir y duomenis, suformuoja train_test_split
        :return:
        """
        cols = self.final_df.columns.to_list()
        X = self.final_df[cols[1:]]
        y = self.final_df['price']
        X_train, X_test, y_train, y_test = \
            train_test_split(X, y, test_size=0.3, random_state=42)
        return X_train, X_test, y_train, y_test

    def train_model(self):
        """
        Patikrina ar modelis jau egzistuoja. Antraip išsitraukia duomenis iš load_model_data() ir
        apmoko linijini regresijos modelį bei paskaičiuoja odelio tikslumą. Paskaičiuoja kiek
        užtruko operacija.Taip pat pirmą kartą leidžiant modelį jis išsaugomas pickle faile
        :return: apmokytas modelis ir tikslumo kooficientas
        """
        try:
            self.model, self.score = pickle.load(open('ALL_MAKES_model.pickle', 'rb'))
            print('modelis uzkrautas')
            return self.model, self.score
        except:
            X_train, X_test, y_train, y_test = self.load_model_data()
            start = perf_counter()
            print('Training started....')
            self.model = LinearRegression().fit(X_train, y_train)
            self.score = self.model.score(X_test, y_test)
            print('Training finished!')
            end = perf_counter()
            load_time = end - start
            self.save_model()
            print(f'New model trained in: {load_time}\nSaved in pickle file!')
            print(f'Models score is: {self.score}')
            print('------------------------------------')
            return self.model, self.score

    def save_model(self):
        """
        išsaugo apmokytą modelį pickle faile
        :return:
        """
        with open(f'ALL_MAKES_model.pickle', 'wb') as f:
            data = [self.model, self.score]
            pickle.dump(data, f)

    def test_model(self):
        """
        Išsitraukia duomenis iš load_model_data() bei atlieka spėjimus. Visą spėjimų info
        suformuoja DataFrame bei išsaugo DB lentelėje 'ALL_MODEL_predictions'
        :return:
        """
        X_train, X_test, y_train, y_test = self.load_model_data()
        test = self.model.predict(X_test)
        spejimai = pd.Series(data=test, name='test_price')
        result_df = pd.concat([y_test.reset_index(), spejimai], axis=1)[['price',
                                                                              'test_price']]
        result_df['diff_%'] = (result_df['price'] - result_df['test_price']) / result_df[
            'test_price'] * 100
        conn = self.connect_to_db()
        result_df.to_sql(name='ALL_MODEL_predictions', con=conn)


def create_params(year, mileage, engine, other):
    """
    Konvertuoja ivestus paremetrus į dummies tinkamus modeliui
    :param year:
    :param mileage:
    :param engine:
    :param other:
    :return: list
    """
    final_df = AutopliusPredictor().create_dataframe()
    df_columns = final_df.columns.to_list()[4:]
    params = [year, mileage, engine]
    for data_df in df_columns:
        if str(data_df) in other:
            params.append(1)
        else:
            params.append(0)
    return params


def filter_ads(make, model, year):
    """
    ištraukia iš DB visus skelbimus atitinkančius markę, modeli ir kainą. Info naudojama
    palyginti modelio kainos spejimą
    :param make:
    :param model:
    :param year:
    :return: DataFrame skelimų
    """
    conn = sqlite3.connect("autoplius_data.sqlite")
    list_of_ads = pd.read_sql_query(f'SELECT * FROM scraped_data_final WHERE make="{str(make)}" AND model="{str(model)}" AND year="{str(year)}"', conn)
    return list_of_ads
