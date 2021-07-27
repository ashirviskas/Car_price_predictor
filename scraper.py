import time
from database import Autoplius, db
from bs4 import BeautifulSoup as bs
import requests
import re
import logging


db.create_all()


class DataScraper:
    """
    Autoplius scrape modulis, kuris identifikuoja kiek viso yra skelbimų ir išsaugo visus
    atitinkančius kriterijus : vairas kairėje, nedaužta faile autoplius_data.sqlite. Saugojama
    info: make, model, type, year, mileage, transmission, engine, fuel, price.
    P.S. dirbama su 20k+ skelbimų, programos trukmė apie 3 valandas.
    """
    def __init__(self):
        self.list = {}
        self.obtain_list()

    def obtain_list(self):
        """
        Iteruojama per visą list markių ir skelbimo skaičių list_of_makes.html faile.
        Apspaičiuojama kiek puslapių reikės krauti kiekvienai markei (į psl telpa 20 skelbimų).
        Info išsaugoma self.obtain_list pagal kurį parsinimo funkcija žinos kiek kiekvieno
        modelio puslapių reikės atidaryt.
        :return: dictionary 'make':'pages'
        """
        data = open('list_of_makes.html', 'r')
        soup = bs(data, 'html.parser')
        rows = soup.find_all('div', 'dropdown-option')
        for each in rows:
            make = each.find(class_='title').get_text()
            count = int(each.find(class_='badge').get_text())
            if count <= 20:
                pages = 1
            else:
                pages = count // 20 + 1
            self.list[make] = pages

    def load_page(self, make, page):
        """
        užkraunamas autoplius puslapis kiekvienai paieškai naudojant make ir page parametrus
        :param make:
        :param page:
        :return:
        """
        url = f'https://autoplius.lt/skelbimai/naudoti-automobiliai/{make}?make_id_list' \
        f'=&engine_capacity_from=&engine_capacity_to=&power_from=&power_to=&kilometrage_from' \
        f'=&kilometrage_to=&has_damaged_id=10924&color_id=&condition_type_id=&make_date_from' \
        f'=&make_date_to=&sell_price_from=&sell_price_to=&fuel_id=&body_type_id=&wheel_drive_id' \
        f'=&euro_id=&fk_place_countries_id=&qt=&qt_autocomplete=&number_of_seats_id' \
        f'=&number_of_doors_id=&gearbox_id=&steering_wheel_id=10922&origin_country_id' \
        f'=&older_not=&order_by=3&order_direction=DESC&slist=1529897967&page_nr={page}'
        self.response = requests.get(url)
        print(f'KRAUNAMAS PUSLAPIS----->{url}')
        return self.response

    def parse_data(self, make):
        """
        Iteruojama per užkrauto puslapio html elementus, sukuriamas skelbimų list kintamajame
        all_ads. Iteruojama per kiekvieną (each) skelbimo html ir ištraukiami skelbimo
        parametrai kaip marke , modelis, metai etc. Įrašoma į DB su self.save_to_db komanda.
        :param make:
        :return:
        """
        data = self.response
        soap = bs(data.text, 'html.parser')
        all_ads = soap.find_all('div', 'announcement-body')
        for each in all_ads:
            try:
                pattern = re.compile(r'\d+.\d+')
                title = each.find(class_='announcement-title').get_text().split()
                if str(title[0]) == str(make):
                    model = str(title[1][:-1])
                else:
                    model = str(title[2][:-1])
                try:
                    engine = float(re.findall(r'\d{1}\.\d{1}', each.find(
                        class_='announcement-title').get_text())[0])
                except:
                    engine = 0
                type = str(title[-1])
                year = int(each.find(attrs={'title': 'Pagaminimo data'}).get_text().split("-")[
                    0].strip())
                fuel = str(each.find(attrs={'title': 'Kuro tipas'}).get_text().strip())
                tran = str(each.find(attrs={'title': 'Pavarų dėžė'}).get_text().strip())
                mileage_raw = each.find(attrs={'title': 'Rida'}).get_text().strip()
                mileage = int(pattern.findall(mileage_raw)[0].replace(' ', ''))
                price_raw = each.find(class_='announcement-pricing-info').get_text().strip()
                price = int(pattern.findall(price_raw)[0].replace(' ', ''))
                try:
                    self.save_to_db(str(make), model, type, year, mileage, tran, engine, fuel, price)
                    print('DATA SAVED!')
                except Exception as e:
                    logging.error(f'Could not save to db: {str(e)}')
                    print('Could not save to db')
            except Exception as e:
                logging.error(f'Praleistas skelbimas, nepakankami duomenys: {str(e)}')
                print('Praleistas skelbimas, nepakankami duomenys')

    def save_to_db(self, *args):
        """
        išsaugojama skelbimo info su args parametrais DB
        :param args:
        :return:
        """
        entry = Autoplius(*args)
        db.session.add(entry)
        db.session.commit()

    def run(self):
        """
        Iteruojamas kiekvienas puslapis pagal markę iš self.list
        :return:
        """
        for make, pages in self.list.items():
            if re.search(r'\s', make):
                make_adj = make.replace(' ', '_')
            elif re.search(r'-', make):
                make_adj = make.replace('-', '_')
            else:
                make_adj = ""
            for page in range(1, pages):
                try:
                    if not make_adj == "":
                        self.load_page(make_adj, page)
                    else:
                        self.load_page(make, page)
                except Exception as e:
                    logging.error(f'load_page error: {str(e)}')
                    print('load_page error')
                try:
                    self.parse_data(make)
                    print(f'Scraped {page} pages in total.')
                except Exception as e:
                    logging.error(f'parse_data error: {str(e)}')
                    print('parse_data error')
                time.sleep(5)


if __name__ == '__main__':
    DataScraper().run()
