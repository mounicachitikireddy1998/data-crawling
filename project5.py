
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os
import re
from zipfile import ZipFile
import shutil
from datetime import datetime, timedelta, date
import numpy as np
from ipdb import set_trace as st
from webdriver_manager.chrome import ChromeDriverManager
from unidecode import unidecode  # to remove unicode chars from string
import asyncio
import aiohttp


current_date = datetime.today().strftime('%Y-%m-%d')
date_dir = os.path.join(os.getcwd(),'RegistryFiles\\ISRCTN',current_date)
download_dir = os.path.join(date_dir,'Downloaded_CSV_File')
#destination_dir = os.path.join(date_dir,'Extracted_japanese_Data')

def download_file():
    """ downloading the zip file from the website """
    try:
        # Construct the URL for the search with the specified date range
        url = f"https://www.isrctn.com/search?q=&filters=GT+dateApplied%3A1998-01-01%2CLE+dateApplied%3A{current_date}"
        # Set up the Chrome web driver and download options
        chrome_options = webdriver.ChromeOptions()
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        p = {"download.default_directory": download_dir} # this will make sure the file gets downloaded in download_dir
        chrome_options.add_experimental_option("prefs", p)
       #chrome_options.add_argument('--headless')
        try:
            with webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options) as driver:
                # Navigate to the website and perform the download
                driver.get(url)
                # Wait for the "Open filters" button to become clickable and then click it
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.opener'))).click()
                # Wait for the "Select all" checkbox to become clickable and then click it
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'select-all'))).click()
                # Wait for the "Download CSV" button to become clickable and then click it
                WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'Btn.Btn--primary.Btn--s.download-csv'))).click()
            print('Download complete')
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)

#download_file()

def read_downloaded_csv_file():
    """ Read the csvfile and Covert downloaded csv file into DataFrame """
    #file_name = ''
    # start_time = datetime.now()
    try:
        for file in os.listdir(download_dir):
            if '.csv' in file:
                file_name = file
        file_path = os.path.join(download_dir,file_name)
        print(file_path)
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(e)
    # finish = datetime.now() - start_time
    # print(finish)

keywords = ['Device','Mixed','Procedure/Surgery','Behavioural','Other',np.NAN]
df =pd.read_csv(r'C:\Users\Venkat.Moram\PycharmProjects\pythonProject1\Medical\ISRCTN\Python_Scripts\RegistryFiles\ISRCTN\2022-12-20\Downloaded_CSV_File\ISRCTN_search_results.csv')
#key = df[df['Intervention type'].str.contains(f'Device|Mixed|Procedure/Surgery|Behavioural|Other|{np.NAN}', case=False) == True]
filtered_df = df.loc[df['Intervention type'].isin(keywords)]
ISRCTN_nos = filtered_df['ISRCTN'].to_list()

async def fetch_page(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            # cookies = response.cookies
            # response = session.get(url, cookies=cookies)
            return await response.text()

async def main():
    tasks = []
    for no in ISRCTN_nos:
        task = asyncio.create_task(fetch_page(f'https://www.isrctn.com/{no}'))
        tasks.append(task)
    htmls = await asyncio.gather(*tasks)
    print(type(htmls),len(htmls))
    # do something with the HTML here

start = time.perf_counter()
asyncio.run(main())
finish = time.perf_counter()-start
print(finish)


def data_crwaling(ISR_Nos):
    ses = HTMLSession()
    c = 0
    for no in ISR_Nos:
        try:
            url = f'https://www.isrctn.com/{no}'
            res = ses.get(url)
            cookies = ses.cookies.get_dict()
            res = ses.get(url, cookies=cookies)
            try:
                unique_id =  res.html.find('span.ComplexTitle_primary',first=True).text.strip()
            except:
                unique_id = ''
            try:
                title = res.html.find('div.ComplexTitle_inner h1',first=True).text.strip()
            except:
                title = ''

            try:
                info_aside = res.html.find('div.Info_aside',first=True)
                overall_trail_status = info_aside.find('dd.Meta_value')[-2].text.strip()
                recruitment_status = info_aside.find('dd.Meta_value')[-3].text.strip()
            except:
                overall_trail_status = ''
                recruitment_status = ''
            try:
                objective = res.html.find('div.Info_main',first=True,containing='Plain English Summary').find('p',first=True).text.split('\nWho can participate?')[0].strip()
            except:
                objective = ''
            try:
                contact_name = res.html.find('div.Info_main',first=True,containing='Plain English Summary').find('p',first=True).text.split('\n')[-1].strip()
            except:
                contact_name = ''

            try:
                primary_contact = res.html.find('div.Info_main',first=True,containing='Primary contact').find('p')[1].text.split('\n')[-1].strip()
            except:
                primary_contact = ''

            try:
                email = res.html.find('div.Info_main',first=True,containing='Primary contact').find('p')[3].text.split('\n')[-1].strip()
            except:
                email = ''

            try:
                telephone = res.html.find('div.Info_main',first=True,containing='Primary contact').find('p')[3].text.split('\n')[-2].strip()
                telephone = (''.join(re.findall('\d+', telephone)).strip())
            except:
                telephone = ''

            try:
                official_title =  res.html.find('div.Info_main',first=True,containing='Study information').find('p')[0].text.strip()
            except:
                official_title = ''

            try:
                acronym = res.html.find('div.Info_main',first=True,containing='Study information').find('p')[1].text.strip()
            except:
                acronym = ''

            try:
                study_hypothesis = res.html.find('div.Info_main',first=True,containing='Study information').find('p')[2].text.strip()
            except:
                study_hypothesis = ''
            try:
                study_design1 = res.html.find('div.Info_main',first=True,containing='Study information').find('p')[4].text.strip()
            except:
                study_design1 = ''
            try:
                study_design2 = res.html.find('div.Info_main', first=True, containing='Study information').find('p')[6].text.strip()
            except:
                study_design2 = ''
            try:
                study_design3 = res.html.find('div.Info_main', first=True,containing='Study information').find('p')[8].text.strip()
            except:
                study_design3 = ''
            try:
                description = res.html.find('div.Info_main', first=True,containing='Study information').find('p')[11].text.strip()
            except:
                description = ''
            try:
                phase = res.html.find('div.Info_main', first=True,containing='Study information').find('p')[13].text.strip()
            except:
                phase = ''
            try:
                primary_outcome = res.html.find('div.Info_main', first=True,containing='Study information').find('p')[15].text.strip()
            except:
                primary_outcome = ''
            try:
                secondary_outcome = res.html.find('div.Info_main', first=True,containing='Study information').find('p')[16].text.strip()
            except:
                secondary_outcome = ''
            try:
                estimated_start_date =  res.html.find('div.Info_main', first=True,containing='Study information').find('p')[-3].text.strip()
            except:
                estimated_start_date = ''
            try:
                estimate_end_date = res.html.find('div.Info_main', first=True, containing='Study information').find('p')[-2].text.strip()
            except:
                estimate_end_date = ''
            try:
                #st()
                inclusion = res.html.find('div.Info_main', containing='Participant inclusion criteria')[-1].find('p')[0].text.strip()
                targets = res.html.find('div.Info_main', containing='Participant inclusion criteria')[-1].find('p')[4].text.strip()
                exclusion = res.html.find('div.Info_main', containing='Participant inclusion criteria')[-1].find('p')[5].text.strip()
            except:
                inclusion = ''
                targets = ''
                exclusion = ''
            print( unique_id,title,overall_trail_status,recruitment_status,objective,sep='\n')
            print(contact_name,primary_contact,email,telephone,study_design1,study_design2,study_design3,sep='\n')
            print(description,phase,primary_outcome,secondary_outcome,estimated_start_date,estimate_end_date,sep='\n')
            print(inclusion,targets,exclusion,sep='\n')
            c+=1
            print(c)
        except Exception as e:
            st()
            print(e)
            print(c)
            print(no)


#data_crwaling(ISRCTN_nos[:100])
