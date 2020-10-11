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

    def get_leaderboard_info(self, competition_ref):
        def parse_submission(submission):
            return {
                'score': submission['score'],
                'date': submission['submissionDate'][:10]
            }
        try:
            leaderboard = self.__api.competition_view_leaderboard(competition_ref)
            submissions = leaderboard['submissions']
            n = len(submissions)
            result = []
            if n == 0:
                return result
            result.append((1, parse_submission(submissions[0])))
            if n == 1:
                return result
            if n > 10:
                result.append((10, parse_submission(submissions[9])))
            result.append((n, parse_submission(submissions[-1])))
            return result
        except Exception:
            return []

    def get_state(self, competition_ref):
        competitions = self.__api.competitions_list(search=competition_ref, page=1)
        if len(competitions) != 1:
            return 'Use the id string of the competition (several competitions were found)'
        competition = competitions[0]
        if competition_ref != competition.ref:
            return 'Use the id string of the competition (requested competition doesn\'t equal to any competition_id)'

        time.sleep(1)
        leaderboard = self.get_leaderboard_info(competition_ref)

        return {
            'title': competition.title,
            'reward': competition.reward,
            'teams': competition.teamCount,
            'days_before_deadline': (competition.deadline - datetime.today()).days,
            'evaluation_metric': competition.evaluationMetric,
            'leaderboard': leaderboard,
            'url': competition.url
        }
