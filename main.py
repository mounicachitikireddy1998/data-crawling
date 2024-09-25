from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import numpy as np
import time 
import os
import re
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager

# Setup current date and directories
current_date = datetime.today().strftime('%Y-%m-%d')
date_dir = os.path.join(os.getcwd(), 'RegistryFiles', 'ISRCTN', current_date)
download_dir = os.path.join(date_dir, 'Downloaded_CSV_File')

if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Keywords for filtering
keywords = ['Device', 'Mixed', 'Procedure/Surgery', 'Behavioural', 'Other', np.nan]
ISRCTN_nos = ["ISRCTN13420346", "ISRCTN99802323"]


def download_file():
    """Downloading the zip file from the website."""
    try:
        url = f"https://www.isrctn.com/search?q=&filters=GT+dateApplied%3A1998-01-01%2CLE+dateApplied%3A{current_date}"
        chrome_options = Options()
        p = {"download.default_directory": download_dir}
        chrome_options.add_experimental_option("prefs", p)
        try:
            with webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options) as driver:
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.opener'))).click()
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'select-all'))).click()
                WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'Btn.Btn--primary.Btn--s.download-csv'))).click()
            print('Download complete')
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)


def read_downloaded_csv_file():
    """Read the csv file and convert downloaded csv file into DataFrame."""
    try:
        for file in os.listdir(download_dir):
            if '.csv' in file:
                file_name = file
        file_path = os.path.join(download_dir, file_name)
        print(file_path)
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(e)


def fetch_page(url):
    session = HTMLSession()
    response = session.get(url)
    return response


def data_crawling(ISRCTN_nos):
    ses = HTMLSession()
    data = []
    for no in ISRCTN_nos:
        record = {}
        try:
            url = f'https://www.isrctn.com/{no}'
            res = ses.get(url)
            cookies = ses.cookies.get_dict()
            res = ses.get(url, cookies=cookies)
            try:
                record['unique_id'] = res.html.find('span.ComplexTitle_primary', first=True).text.strip()
            except:
                record['unique_id'] = ''
            try:
                record['title'] = res.html.find('div.ComplexTitle_inner h1', first=True).text.strip()
            except:
                record['title'] = ''

            try:
                info_aside = res.html.find('div.Info_aside', first=True)
                record['overall_trail_status'] = info_aside.find('dd.Meta_value')[-2].text.strip()
                record['recruitment_status'] = info_aside.find('dd.Meta_value')[-3].text.strip()
            except:
                record['overall_trail_status'] = ''
                record['recruitment_status'] = ''
            try:
                record['objective'] = \
                res.html.find('div.Info_main', first=True, containing='Plain English Summary').find('p',
                                                                                                    first=True).text.split(
                    '\nWho can participate?')[0].strip()
            except:
                record['objective'] = ''
            try:
                record['contact_name'] = \
                res.html.find('div.Info_main', first=True, containing='Plain English Summary').find('p',
                                                                                                    first=True).text.split(
                    '\n')[-1].strip()
            except:
                record['contact_name'] = ''

            try:
                record['primary_contact'] = \
                res.html.find('div.Info_main', first=True, containing='Primary contact').find('p')[1].text.split('\n')[
                    -1].strip()
            except:
                record['primary_contact'] = ''

            try:
                record['email'] = \
                res.html.find('div.Info_main', first=True, containing='Primary contact').find('p')[3].text.split('\n')[
                    -1].strip()
            except:
                record['email'] = ''

            try:
                record['telephone'] = \
                res.html.find('div.Info_main', first=True, containing='Primary contact').find('p')[3].text.split('\n')[
                    -2].strip()
                record['telephone'] = (''.join(re.findall('\d+', record['telephone'])).strip())
            except:
                record['telephone'] = ''

            try:
                record['official_title'] = \
                res.html.find('div.Info_main', first=True, containing='Study information').find('p')[0].text.strip()
            except:
                record['official_title'] = ''

            try:
                record['acronym'] = \
                res.html.find('div.Info_main', first=True, containing='Study information').find('p')[1].text.strip()
            except:
                record['acronym'] = ''

            try:
                record['study_hypothesis'] = \
                res.html.find('div.Info_main', first=True, containing='Study information').find('p')[2].text.strip()
            except:
                record['study_hypothesis'] = ''
            try:
                record['study_design1'] = \
                res.html.find('div.Info_main', first=True, containing='Study information').find('p')[4].text.strip()
            except:
                record['study_design1'] = ''
            try:
                record['study_design2'] = \
                res.html.find('div.Info_main', first=True, containing='Study information').find('p')[6].text.strip()
            except:
                record['study_design2'] = ''
            try:
                record['study_design3'] = \
                res.html.find('div.Info_main', first=True, containing='Study information').find('p')[8].text.strip()
            except:
                record['study_design3'] = ''
            try:
                record['description'] = \
                res.html.find('div.Info_main', first=True, containing='Study information').find('p')[11].text.strip()
            except:
                record['description'] = ''
            try:
                record['phase'] = res.html.find('div.Info_main', first=True, containing='Study information').find('p')[
                    13].text.strip()
            except:
                record['phase'] = ''
            try:
                record['primary_outcome'] = \
                res.html.find('div.Info_main', first=True, containing='Study information').find('p')[15].text.strip()
            except:
                record['primary_outcome'] = ''
            try:
                record['secondary_outcome'] = \
                res.html.find('div.Info_main', first=True, containing='Study information').find('p')[16].text.strip()
            except:
                record['secondary_outcome'] = ''
            try:
                record['estimated_start_date'] = \
                res.html.find('div.Info_main', first=True, containing='Study information').find('p')[-3].text.strip()
            except:
                record['estimated_start_date'] = ''
            try:
                record['estimate_end_date'] = \
                res.html.find('div.Info_main', first=True, containing='Study information').find('p')[-2].text.strip()
            except:
                record['estimate_end_date'] = ''
            try:
                record['inclusion'] = \
                res.html.find('div.Info_main', containing='Participant inclusion criteria')[-1].find('p')[
                    0].text.strip()
                record['targets'] = \
                res.html.find('div.Info_main', containing='Participant inclusion criteria')[-1].find('p')[
                    4].text.strip()
                record['exclusion'] = \
                res.html.find('div.Info_main', containing='Participant inclusion criteria')[-1].find('p')[
                    5].text.strip()
            except:
                record['inclusion'] = ''
                record['targets'] = ''
                record['exclusion'] = ''

            data.append(record)
            print(record)
        except Exception as e:
            print(e)
            print(no)

    df = pd.DataFrame(data)
    df.to_excel(os.path.join(date_dir, 'ISRCTN_data.xlsx'), index=False)
    print(f"Data saved to {os.path.join(date_dir, 'ISRCTN_data.xlsx')}")


if __name__ == "__main__":
    data_crawling(ISRCTN_nos[:2])