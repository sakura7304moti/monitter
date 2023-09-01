from . import const,utils,sqlite
from tqdm import tqdm
holoList = const.holoList()

class Scraper:
    def base_scraper(self, query: str, date: int = 30, limit: int = 3000):
        driver = utils.get_driver(False)
        df = utils.get_tweet(query,limit,date,driver)
        sqlite.update(df,query,'base')
        driver.close()
        
    def holo_scraper(self, date: int = 30, limit: int = 3000):
        driver = utils.get_driver(False)
        for query in tqdm(holoList,desc="holo scraper"):
            print(f'Fanart : {query}')
            df = utils.get_tweet(query,limit,date,driver)
            sqlite.update(df,query,'holo')
        driver.close()