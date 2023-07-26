from src import moti,utils,const

try:
    utils.message("scheduler start")
    model = moti.Scraper()
    option = const.option_sc()
    tag = const.hashtags()
    """
    BASE
    """
    date, limit = option.base_option()
    hashtags = tag.base_hashtags()
    for p in hashtags:
        model.base_scraper(p, date, limit)
    """
    HOLO
    """
    date, limit = option.holo_option()
    model.holo_scraper(date, limit)
    """
    USER
    """
    utils.message("scheduler end")
except Exception as e:
    print(e)
    utils.message(e)