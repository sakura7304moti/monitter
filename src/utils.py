#Import-------------------------------------------------------------------------------
from io import StringIO, BytesIO
import os
import re
from time import sleep
import random
from urllib import request
import requests
import chromedriver_autoinstaller
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service
import datetime
import pandas as pd
import platform
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import urllib
from urllib.parse import quote
#--------------------------------------------------------------------------------------

def message(text: str):
    try:
        # 取得したTokenを代入
        line_notify_token = "bLg2L6w7MhUXm5eG1Pyz6jB5IJ8PVU3anYX5FbjUbSc"

        # 送信したいメッセージ
        message = text

        # Line Notifyを使った、送信部分
        line_notify_api = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": f"Bearer {line_notify_token}"}
        data = {"message": f"{message}"}
        requests.post(line_notify_api, headers=headers, data=data)
    except:
        pass

def get_driver(headless=True):
    options = ChromeOptions()
    if headless is True:
        print("Scraping on headless mode.")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")  # An error will occur without this line
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        options.headless = True
    else:
        options.headless = False
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
    try:
        driver_path = chromedriver_autoinstaller.install()
        service = Service(executable_path=driver_path)
        # サービスを起動
        driver = webdriver.Chrome(options=options,service=service)
    except Exception as e:
        print('err -> ',e)
        driver = webdriver.Chrome(options=options)
    return driver

def get_url(query:str)-> str:
    parsed = quote(query)
    url = f'https://nitter.net/search?f=tweets&q={parsed}&f-media=on&f-images=on&e-replies=on&e-nativeretweets=on'
    return url

def get_image_url(url:str) -> str:
    base = url.split('%2F')[-1]
    ext = base.split('.')[-1]
    file_name=base.replace(f'.{ext}','')
    twitter_url = f'https://pbs.twimg.com/media/{file_name}?format={ext}&name=orig'
    return twitter_url


def get_tweet(query:str,limit:int,date:int,driver):
    print(f'url -> {get_url(query)}')
    driver.get(get_url(query))
    # Get Screen Shot
    driver.save_screenshot('test.png')
    print('saved sc')

    # 現在の日時を取得
    now = datetime.datetime.now()
    date_time = datetime.datetime.now()
    tweets = []
    while(True):
        try:
            # ページのHTMLを取得
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            timeline_items = soup.find_all('div', class_='timeline-item')
            
            #1ページ分の処理-----------------------------------------------------------
            for item in timeline_items:
                if len(item.find_all('a')) > 1:
                    url = 'https://nitter.net' + item.find('a',class_='tweet-link')['href']#ツイート元URL
                    base_images = ['https://nitter.net' + a['href'] for a in item.find_all('a',class_='still-image')]#nitterの画像URL
                    images = [get_image_url(image) for image in base_images]
                    # フォーマットを指定してdatetimeに変換
                    date_str = item.find('span',class_='tweet-date').find('a')['title']
                    date_format = "%b %d, %Y · %I:%M %p %Z"
                    date_time = datetime.datetime.strptime(date_str, date_format)
                    user_name = item.find('a',class_='username')['title']#ユーザーID
                    display_name = item.find('a',class_='fullname')['title']#表示ユーザー名
                    # icon-heartクラスを持つ要素を取得
                    like_count = 0
                    sub_items = item.find_all('span',class_='tweet-stat')
                    for i in sub_items:
                        icon_heart_element = i.find('span', class_='icon-heart')
                        if icon_heart_element is not None:
                            try:
                                like_count = int(i.get_text(strip=True).replace(' ', '').replace(',', ''))#いいね
                            except:
                                pass
                    data = [
                        url,
                        images,
                        date_time,
                        user_name,
                        display_name,
                        like_count
                    ]
                    if like_count >= 10:
                        tweets.append(data)
            #1ページ分の処理END-----------------------------------------------------------
            
            #----- 検索を続行するか判別-----
            if len(tweets) > limit:
                print('limit over')
                break
            if (now - date_time).days > date:
                print('date over')
                break
            print(f'LIMIT : {len(tweets)}/{limit} | DATE : {(now - date_time).days} / {date}')
            #------------------------------
            #Load moreをクリック
            try:
                # 1から3の間のランダムな浮動小数点数を取得
                random_value = random.uniform(1, 3)
                sleep(random_value)
                driver.find_element(By.LINK_TEXT,"Load more").click()
            except:
                break
        except Exception as e:
            print(e)
            pass
            
    # breakしたら、データフレームにして保存する
    print(f'saved image : {len(tweets)}')
    message(f'saved image : {len(tweets)}')
    tweet_df = pd.DataFrame(
        tweets, columns=["url", "images", "date", "userId", "userName", "likeCount"]
    )
    return tweet_df

def download(url,save_path):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0" )
    response = urllib.request.urlopen(req)
    with open(save_path, "wb") as f:
        f.write(response.read())