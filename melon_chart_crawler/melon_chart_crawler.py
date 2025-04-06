import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import time

import pandas as pd

from os import listdir

url = 'https://www.melon.com/chart/index.htm'

options = Options()
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
options.add_argument("lang=ko_KR") 
options.add_experimental_option('excludeSwitches', ['enable-logging'])


this_year = datetime.now().year

if listdir('./output/') == []:
    print('No chart files found.')
    latest_chart_year = 2000
    latest_chart_month = 1
else:
    latest_chart = listdir('./output/')[-1]
    print(latest_chart)

    latest_chart_year = int(latest_chart[:4])
    latest_chart_month = int(latest_chart[5:7])



def read_table(tr_list):
    song_info_list = list()
    for tr in tr_list:
        # td_list = tr.find_elements_by_tag_name('td')
        td_list = WebDriverWait(tr, 15).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'td'))
        )
        
        td_rank = td_list[1]
        rank_class = WebDriverWait(td_rank, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'rank'))
        )
        WebDriverWait(rank_class, 25).until(lambda rank_class: rank_class.text.strip() != '')
        # if len(td_rank.find_element_by_class_name('rank').text.strip()) == 0:
        #     print(td_rank.find_element_by_class_name('rank').text)
        rank = int(
            # td_rank.find_element_by_class_name('rank').text
            WebDriverWait(td_rank, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'rank'))
            ).text.strip()
        )

        td_img = td_list[2]
        # album_id = int(td_img.find_element_by_tag_name('a').get_attribute('href').split("'")[1])
        album_id = int(
            WebDriverWait(td_img, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, 'a'))
            ).get_attribute('href').split("'")[1]
        )
        # album_img = td_img.find_element_by_tag_name('img').get_attribute('src').replace('/melon/resize/48/quality/80/optimize', '')
        album_img = WebDriverWait(td_img, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, 'img'))
        ).get_attribute('src').replace('/melon/resize/48/quality/80/optimize', '')

        td_song_info = td_list[3]
        # a_tag_list = td_song_info.find_elements_by_tag_name('a')
        a_tag_list = WebDriverWait(td_song_info, 15).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'a'))
        )

        song_id = int(a_tag_list[0].get_attribute('href').split("'")[1])
        song_title = a_tag_list[1].text

        if len(a_tag_list) >= 3:
            artist_name = a_tag_list[2].text
            artist_id = int(a_tag_list[2].get_attribute('href').split("'")[1])
        else:
            artist_name = None
            artist_id = None

        song_info_list.append([rank, album_id, song_id, song_title, artist_name, artist_id])
    
    df = pd.DataFrame(
        song_info_list, 
        columns=['rank', 'album_id', 'song_id', 'song_title', 'artist_name', 'artist_id']
    )
    
    return df


def read_chart_and_write_dataframe(driver, page_info, top_n):
    # search_cnt = driver.find_element_by_id('serch_cnt')
    search_cnt = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, 'serch_cnt'))
    )

    # wait until search_cnt.text contains '~'
    WebDriverWait(search_cnt, 15).until(
        lambda search_cnt: '~' in search_cnt.text
    )

    chart_name = search_cnt.text.replace('.', '_').replace(' ~ ', '__')
    file_path = f'./output/{chart_name}__{page_info}.txt'
    print(chart_name)


    # chartListObj = driver.find_element_by_id('chartListObj')
    chartListObj = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, 'chartListObj'))
    )
    
    # tr_list = chartListObj.find_elements_by_class_name(f'lst{top_n}')
    tr_list = WebDriverWait(chartListObj, 15).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, f'lst{top_n}'))
    )
    # tr_list = WebDriverWait(chartListObj, 15).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'tr')))
    df_top50 = read_table(tr_list)

    # pagination = driver.find_element_by_class_name('paginate')
    
    
    
    

        
    
    df_top50.to_csv(file_path, sep='|', index=False)

    return driver
            



with webdriver.Chrome(options=options) as driver:
    driver.get(url=url)

    driver.implicitly_wait(15)

    # gnb_menu = driver.find_element_by_xpath('//*[@class="btn_chart_f"]')
    gnb_menu = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, '//*[@class="btn_chart_f"]'))
    )
    gnb_menu.click()

    # driver.find_element_by_xpath('//a[@data-value="WE"]').click()
    driver.find_element(By.XPATH, '//a[@data-value="WE"]').click()


    
    decade_list = [2000, 2010, 2020]

    

    for d in decade_list:
        # di = driver.find_element_by_xpath(f'//div[contains(@class, "box_chic nth1 view")]/div[@class="list_value"]//input[@value="{d}"]')
        di = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH,f'//div[contains(@class, "box_chic nth1 view")]/div[@class="list_value"]//input[@value="{d}"]'))
        )
        # di.find_element_by_xpath('..').click()
        di.find_element(By.XPATH, '..').click()

        print(f'# {d} #######')

        years = [y for y in range(d, d+10)]

        for y in years:
            if y > this_year:
                break

            if y < latest_chart_year:
                print('Already got chart in year: ', y)
                continue

            # year_input = driver.find_element_by_xpath(f'//div[contains(@class, "box_chic nth2 view")]/div[@class="list_value"]//input[@value="{y}"]/..')
            year_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH,f'//div[contains(@class, "box_chic nth2 view")]/div[@class="list_value"]//input[@value="{y}"]/..'))
            )
            # year_input.find_element_by_xpath('..').click()
            year_input.click()

            for m in range(1, 13):
                if y == latest_chart_year and m < latest_chart_month:
                    print(f'Already got chart of {y} {m}')
                    continue

                m = f'0{m}' if m < 10 else m
                # month_input = driver.find_element_by_xpath(f'//div[contains(@class, "box_chic nth3 view")]/div[@class="list_value"]//input[@value="{m}"]')
                month_input = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH,f'//div[contains(@class, "box_chic nth3 view")]/div[@class="list_value"]//input[@value="{m}"]'))
                )

                # month_input.find_element_by_xpath('..').click()
                month_input.find_element(By.XPATH, '..').click()

                # week_inputs = driver.find_elements_by_xpath(f'//div[contains(@class, "box_chic nth4 view")]/div[@class="list_value"]//input')
                week_inputs = WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.XPATH,f'//div[contains(@class, "box_chic nth4 view")]/div[@class="list_value"]//input'))
                )

                for wi in week_inputs:
                    # wi.find_element_by_xpath('..').click()
                    wi.find_element(By.XPATH, '..').click()

                    # genre = driver.find_element_by_xpath(f'//div[contains(@class, "box_chic last view")]/div[@class="list_value"]//input[@id="gnr_1"]/..')
                    # genre.find_element_by_xpath('..').click()
                    genre = WebDriverWait(driver, 15).until(
    	                EC.presence_of_element_located((By.XPATH,f'//div[contains(@class, "box_chic last view")]/div[@class="list_value"]//input[@id="gnr_1"]/..'))
                    )
                    genre.click()

                    # driver.find_element_by_xpath('//div[@class="wrap_btn_serch"]/button[@type="submit"]').click()
                    driver.find_element(By.XPATH, '//div[@class="wrap_btn_serch"]/button[@type="submit"]').click()
                    
                    time.sleep(0.5)

                    driver = read_chart_and_write_dataframe(driver, '__01_50', 50)

                    pagination = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'page_num')))

                    print('--------------------------------')

                    
                    if '51 - 100' in pagination.text:
                        # pagination.find_element_by_tag_name('a').click()
                        pagination.find_element(By.TAG_NAME, 'a').click()
                        driver = read_chart_and_write_dataframe(driver, '__50_100', 100)
                        print('############## 51 to 100 #############################')
     


    print(decade_list)
    print('Finished')
    # time.sleep(5)
