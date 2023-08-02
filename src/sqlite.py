"""
CREATE DB
CREATE TABLE
INSERT DB
SEARCH
SEARCH COUNT
"""
from . import const
output = const.Output()

"""
CREATE DB
"""
import sqlite3
# sns.dbを作成する
# すでに存在していれば、それにアスセスする。
dbname = output.sqlite_db()
conn = sqlite3.connect(dbname)

# データベースへのコネクションを閉じる。(必須)
conn.close()

"""
CREATE TABLE
"""
conn = sqlite3.connect(dbname)
# sqliteを操作するカーソルオブジェクトを作成
cur = conn.cursor()

# personsというtableを作成してみる
# 大文字部はSQL文。小文字でも問題ない。
cur.execute(
    """CREATE TABLE IF NOT EXISTS twitter(
            hashtag STRING,
            mode STRING,
            url STRING,
            date STRING,
            images STRING,
            userId INTEGER,
            userName STRING,
            likeCount INTEGER
            )
            """)

# データベースへコミット。これで変更が反映される。
conn.commit()
conn.close()

"""
UNIQUE DELETE
"""
def remove_duplicates():
    # データベースに接続する
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()

    # 重複をチェックして削除するクエリを実行
    query = """
    DELETE FROM twitter
    WHERE rowid NOT IN (
        SELECT MIN(rowid) 
        FROM twitter 
        GROUP BY url, hashtag
    )
    """
    cursor.execute(query)

    # 変更をコミットし、接続を閉じる
    conn.commit()
    conn.close()

"""
INSERT
"""
import re
import pandas as pd
import os
from tqdm import tqdm
import datetime
from . import const
from . import utils
output = const.Output()

def update(df,hashtag:str,mode:str):
    utils.message(f'update start {hashtag}')
    # 正規表現パターン
    pattern = r'[\'"\[\]]'

    # データベースに接続する
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    
    # レコードの存在をチェックするためのクエリを作成する
    check_query = f"SELECT * FROM twitter WHERE hashtag = '{hashtag}'"

    # クエリを実行して結果を取得する
    cursor.execute(check_query)
    result = cursor.fetchall()

    #hashtag + URL のリストを作成
    if result is None:
        hash_list = []
        url_list = []
    else:
        hash_list = [r[0]+r[2] for r in result]
        url_list = [r[2] for r in result]
    
    for index,row in tqdm(df.iterrows(),total=len(df),desc='UPDATE'):

        #要素の取得
        url = row['url']
        date = row['date'].strftime("%Y-%m-%d")
        #date = date.split(' ')[0]
        images = str(row['images'])
        images = re.sub(pattern,'',images)
        userId = row['userId']
        userName = row['userName']
        try:
            userName = re.sub(pattern,'',userName)
        except:
            userName = ''
        likeCount = int(row['likeCount'])
        
        # レコードが存在しない場合は追加、存在する場合は更新する
        #if hashtag + url not in hash_list:
        if url not in url_list:    
            # レコードを追加するクエリを作成する
            insert_query = f"""
                INSERT INTO twitter (hashtag,mode,url,date,images,userId,userName,likeCount) 
                VALUES (:hashtag,:mode,:url,:date,:images,:userId,:userName,:likeCount)"""
            args = {
                'hashtag':hashtag,
                'mode':mode,
                'url':url,
                'date':date,
                'images':images,
                'userId':userId,
                'userName':userName,
                'likeCount':likeCount
            }
            # レコードを追加する
            cursor.execute(insert_query,args)
        else:
            # レコードを追加するクエリを作成する
            update_query = f"""
            UPDATE twitter SET
                hashtag = :hashtag,
                mode = :mode,
                url = :url,
                date = :date,
                images = :images,
                userId = :userId,
                userName = :userName,
                likeCount = :likeCount
            WHERE url = :url"""
            args = {
                'hashtag':hashtag,
                'mode':mode,
                'url':url,
                'date':date,
                'images':images,
                'userId':userId,
                'userName':userName,
                'likeCount':likeCount
            }
            # レコードを更新する
            cursor.execute(update_query,args)
        
    # 変更をコミットし、接続を閉じる
    conn.commit()
    conn.close()


    #重複したレコードを削除する(とりあえずの対処)
    remove_duplicates()
    utils.message(f'update finish {hashtag}')

"""
SELECT PAGE
"""
def searchQuery(
        page_no:int=1,
        page_size:int=30,
        hashtag:str='',
        start_date:str='',
        end_date:str='',
        user_name:str='',
        mode:str='',
        min_like:int=0,
        max_like:int=0
):
    #ページング設定
    offset = (max(page_no - 1,0))*page_size  

    query = "SELECT * FROM twitter where 1 = 1 "
    if hashtag != '':
        query = query + "and hashtag like :hashtag "
    if start_date != '' and end_date != '':
        query = query + "and date BETWEEN :start_date AND :end_date "
    if user_name != '':
        query = query + "and userId = :user_name "
    if mode != '':
        query = query + "and mode = :mode "
    if min_like != 0:
        query = query + "and likeCount >= :min_like "
    if max_like != 0:
        query = query + "and :max_like >= likeCount "
    query = query + 'order by date desc,url '
    if page_size != 0:
        limit_sql = 'limit :page_size offset :offset'
        query = query + limit_sql
        
    args = {
        'hashtag':f'%{hashtag}%',
        'start_date':start_date,
        'end_date':end_date,
        'user_name':user_name,
        'mode':mode,
        'min_like':min_like,
        'max_like':max_like,
        'page_size':page_size,
        'offset':offset
    }
    return query,args


def search(
        page_no:int=1,
        page_size:int=30,
        hashtag:str='',
        start_date:str='',
        end_date:str='',
        user_name:str='',
        mode:str='',
        min_like:int=0,
        max_like:int=0
) -> list[const.TwitterQueryRecord]:
    # データベースに接続する
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()

    # SELECTクエリを実行
    query,args = searchQuery(
        page_no,
        page_size,
        hashtag,
        start_date,
        end_date,
        user_name,
        mode,
        min_like,
        max_like
    )
    cursor.execute(query,args)
    results = cursor.fetchall()

    # 結果を表示
    records = []
    for row in results:
        rec = const.TwitterQueryRecord(*row)
        records.append(rec)

    # 接続を閉じる
    conn.close()
    return records

"""
SEARCH COUNT
"""
def search_count(
        hashtag:str='',
        start_date:str='',
        end_date:str='',
        user_name:str='',
        mode:str='',
        min_like:int=0,
        max_like:int=0
):
    query,args = searchQuery(
        1,
        0,
        hashtag,
        start_date,
        end_date,
        user_name,
        mode,
        min_like,
        max_like)
    
    # データベースに接続する
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()

    #件数のみ取得
    count_query = f'select count(*) from ({query})'
    cursor.execute(count_query,args)
    results = cursor.fetchall()

    return results[0][0]