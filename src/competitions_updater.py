from kaggle.api.kaggle_api_extended import KaggleApi
import time
from datetime import datetime


class CompetitionUpdater(object):
    def __init__(self, from_date):
        self.__api = KaggleApi()
        self.__api.authenticate()
        self.__from_date = from_date

    # return all competitions in [from_date, query_date) interval
    def get_new_competitions(self, query_date):
        def parse_competition(c):
            return {
                'id': c.ref,
                'title': c.title,
                'category': c.category,
                'days_before_deadline': (c.deadline - datetime.today()).days,
                'tags': c.tags,
                'url': c.url
            }

        results = []
        page = 1
        last_enabled_date = query_date

        while last_enabled_date >= self.__from_date:
            competitions = self.__api.competitions_list(sort_by='recentlyCreated', page=page)
            for c in competitions:
                current_date = c.enabledDate
                if query_date > current_date >= self.__from_date:
                    results.append(parse_competition(c))
            last_enabled_date = competitions[-1].enabledDate
            page += 1
            time.sleep(1)

        self.__from_date = query_date

        return results
