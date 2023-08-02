import os
import pandas as pd
import yaml
import glob
import json

# プロジェクトの相対パス
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# hololive fanart tag list
def holoList():
    holo_path = os.path.join(base_path, "option", "HoloFanArt.csv")
    df = pd.read_csv(holo_path, index_col=0)
    word_list = df["FanArt"].tolist()
    return word_list

def _output() -> dict:
    yaml_path = os.path.join(base_path, "option", "output.yaml")
    with open(yaml_path) as file:
        yml = yaml.safe_load(file)
    return yml


# 各保存先
class Output:
    def __init__(self):
        self._base_path = base_path
        self._yml = _output()
        # make folders
        if not os.path.exists(self._yml["base"]["database"]):
            os.makedirs(self._yml["base"]["database"])
        if not os.path.exists(self._yml["base"]["image"]):
            os.makedirs(self._yml["base"]["image"])

        if not os.path.exists(self._yml["holo"]["database"]):
            os.makedirs(self._yml["holo"]["database"])
        if not os.path.exists(self._yml["holo"]["image"]):
            os.makedirs(self._yml["holo"]["image"])

        if not os.path.exists(self._yml["user"]["database"]):
            os.makedirs(self._yml["user"]["database"])
        if not os.path.exists(self._yml["user"]["image"]):
            os.makedirs(self._yml["user"]["image"])

    def base_database(self, query: str):
        return os.path.join(
            self._base_path, self._yml["base"]["database"], f"{query}_database.csv"
        )

    def base_image(self, query: str):
        return os.path.join(self._base_path, self._yml["base"]["image"], f"{query}")

    def holo_database(self, query: str):
        return os.path.join(
            self._base_path, self._yml["holo"]["database"], f"{query}_database.csv"
        )

    def holo_image(self, query: str):
        return os.path.join(self._base_path, self._yml["holo"]["image"], f"{query}")

    def user_database(self, userName: str):
        return os.path.join(
            self._base_path, self._yml["user"]["database"], f"{userName}_database.csv"
        )

    def user_image(self, userName: str):
        return os.path.join(self._base_path, self._yml["user"]["image"], f"{userName}")

    def sqlite_db(self):
        return os.path.join(self._base_path, "sns.db")

    def database_list(self):
        files = glob.glob(
            os.path.join(self._base_path, "Data", "Twitter", "*", "Database", "*.csv")
        )
        return files

# スケジューラーで取得するハッシュタグ
class hashtags:
    def base_hashtags(self):
        csv_path = os.path.join(base_path, "option", "base_sc.csv")
        df = pd.read_csv(csv_path)
        return df["hashtag"].to_list()

    def holo_hashtags(self):
        return holoList()
    
# Option--------------------------------------------------
class options:
    limit_date = 30
    limit_tweets = 3000


def _option_sc() -> dict:
    yaml_path = os.path.join(base_path, "option", "sc_option.yaml")
    with open(yaml_path) as file:
        yml = yaml.safe_load(file)
    return yml


class option_sc:
    def __init__(self):
        self._yml = _option_sc()

    def _get_option(self, key: str):
        date = self._yml[key]["date"]
        limit = self._yml[key]["limit"]
        return date, limit

    def base_option(self):
        return self._get_option("base")

    def holo_option(self):
        return self._get_option("holo")

    def user_option(self):
        return self._get_option("user")


class api_option:
    def __init__(self):
        self._json_path = os.path.join(base_path, "option", "config.json")
        # ファイルを開いてJSONデータを読み取る
        with open(self._json_path, "r") as file:
            json_data = json.load(file)
        self.PAGE_SIZE: int = json_data.get("PAGE_SIZE", 0)


# QueryRecord---------------------------------------------
import sqlite3
import datetime


class TwitterQueryRecord:
    hashtag: str
    mode: str
    url: str
    date: datetime.date
    images: list[str]
    userId: str
    userName: str
    likeCount: int

    def __init__(
        self,
        hashtag: str,
        mode: str,
        url: str,
        date: str,
        images: str,
        userId: str,
        userName: str,
        likeCount: int,
    ):
        self.hashtag = hashtag
        self.mode = mode
        self.url = url
        self.date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        self.images = images.split(",")
        self.userId = userId
        self.userName = userName
        self.likeCount = likeCount

    def __str__(self):
        return (
            f"Hashtag: {self.hashtag}\n"
            f"Mode: {self.mode}\n"
            f"URL: {self.url}\n"
            f"Date: {self.date}\n"
            f"Images: {self.images}\n"
            f"User ID: {self.userId}\n"
            f"User Name: {self.userName}\n"
            f"Like Count: {self.likeCount}\n"
        )

    def __dict__(self):
        return {
            "hashtag": self.hashtag,
            "mode": self.mode,
            "url": self.url,
            "date": self.date.strftime("%Y-%m-%d"),
            "images": self.images,
            "userId": self.userId,
            "userName": self.userName,
            "likeCount": self.likeCount,
        }
