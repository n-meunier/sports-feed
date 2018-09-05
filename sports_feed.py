from BeautifulSoup import BeautifulSoup
import re
import os
import urllib2
import pandas as pd
from datetime import datetime, date, timedelta
import ConfigParser

pattern = r'javascript:pop.*,\'(.*)-vs-(.*)\/(\d{2}-\d{2}-\d{4})\''
col = ['date', 'team-home', 'team-away', 'score-home', 'score-away']

config = ConfigParser.ConfigParser()
config.read('sports_config.cfg')
LINK_LIGUE1 = config.get('links', 'link_ligue1')
LINK_TOP14 = config.get('links', 'link_top14')
LINK_NBA = config.get('links', 'link_nba')
LINK_C1 = config.get('links', 'link_c1')

yesterday = date.today() - timedelta(4)
yesterday_format = yesterday.strftime('%a %d %b %Y')
y_df_format = yesterday.strftime('%d-%m-%Y')


# -------------------- FUNCTIONS ------------------------------------------------
def get_results_1(link, df):
    """ Return a dataframe with the game results on from a link with data in
    format 1.
    :param link: url to the website
    :param df: Dataframe to fill
    :return: updated dataframe
    """
    page = urllib2.urlopen(link).read()
    soup = BeautifulSoup(page)

    for t in soup.findAll('p', text=re.compile("(\w{3} \d{2} \w{3} \d{4})")):
        date = datetime.strptime(t, '%a %d %b %Y').strftime('%d-%m-%Y')
        # print date

        try:
            div = t.findNext('div')
            for table in div.findAll('table'):
                for p in table.findAll('span'):
                    if p.get('title'):
                        if 'AOT' in p.text or 'FT' in p.text:
                            # print p.text
                            # print 'game'
                            game = p.findParent('tr')
                            for q in game.findAll('td'):
                                # print q
                                if q.get('class') and 'home' in q.get('class'):
                                    hteam = q.text
                                    # print('team-home: %s' % hteam)
                                if q.get('class') and 'away' in q.get('class'):
                                    ateam = q.text
                                    # print('team-away: %s' % ateam)
                                if q.get('class') and 'score' in q.get('class'):
                                    score = re.match('(\d) - (\d)', q.text)
                                    hscore = score.group(1)
                                    ascore = score.group(2)
                                    # print('score-home: %s' % hscore)
                                    # print('score-away: %s' % ascore)
                            df = df.append({'date': date,
                                            'team-home': hteam,
                                            'team-away': ateam,
                                            'score-home': hscore,
                                            'score-away': ascore},
                                           ignore_index=True)
        except AttributeError as error:
            print('No data for %s' % str(date))
            print(error)

    df = df.drop_duplicates(['date', 'team-home']).reset_index(drop=True)
    return df


def get_results_2(link, df):
    """ Return a dataframe with the game results on from a link with data in
    format 2.
    :param link: url to the website
    :param df: Dataframe to fill
    :return: updated dataframe
    """
    page = urllib2.urlopen(link).read()
    soup = BeautifulSoup(page)

    for t in soup.findAll('p', text=re.compile("(\w{3} \d{2} \w{3} \d{4})")):
        date = datetime.strptime(t, '%a %d %b %Y').strftime('%d-%m-%Y')

    # foundtext = soup.find('p', text=yesterday_format)
        try:
            # div = foundtext.findNext('div')
            div = t.findNext('div')
            # table = foundtext.findNext('table')
            for table in div.findAll('table'):
                for p in table.findAll('span'):
                    if p.get('title'):
                        if 'AOT' in p.text or 'FT' in p.text:
                            # print p.text
                            team_1 = p.findParent('tr')
                            # print 'TEAM 1'
                            # print team_1
                            for q in team_1.findAll('td'):
                                # print q
                                if q.get('class') and 'hometeam' in q.get('class'):
                                    hteam = (re.match('.*;(.*)', q.text)).group(1)
                                    # print('team-home: %s' % hteam)
                                if q.get('class') and 'ts_setB' in q.get('class'):
                                    hscore = (re.match('.*;(\d+)', q.text)).group(1)
                                    # print('score-home: %s' % hscore)
                            team_2 = team_1.findNext('tr')
                            # print 'TEAM 2'
                            # print team_2
                            for q in team_2.findAll('td'):
                                # print q
                                if q.get('class') and 'awayteam' in q.get('class'):
                                    ateam = (re.match('.*;(.*)', q.text)).group(1)
                                    # print('team-away: %s' % ateam)
                                if q.get('class') and 'ts_setB' in q.get('class'):
                                    ascore = (re.match('.*;(\d+)', q.text)).group(1)
                                    # print('score-away: %s' % ascore)
                            df = df.append({'date': date,
                                            'team-home': hteam,
                                            'team-away': ateam,
                                            'score-home': hscore,
                                            'score-away': ascore},
                                           ignore_index=True)
        except AttributeError as error:
            print('No data for %s' % str(date))
            print(error)
    df = df.drop_duplicates(['date', 'team-home']).reset_index(drop=True)
    return df


# -------------------- MAIN -----------------------------------------------------
# FOOT - Ligue 1
csv_file = os.path.abspath(os.path.dirname(__file__)) + '/results-ligue1.csv'
if os.path.isfile(csv_file):
    df_ligue1 = pd.read_csv(csv_file, sep=';', index_col=0)
else:
    df_ligue1 = pd.DataFrame(columns=col)

df_ligue1 = get_results_1(LINK_LIGUE1, df_ligue1)
print df_ligue1

df_ligue1.to_csv('results-ligue1.csv', sep=';', encoding='utf-8')

# FOOT - Champions League
csv_file = os.path.abspath(os.path.dirname(__file__)) + '/results-c1.csv'
if os.path.isfile(csv_file):
    df_c1 = pd.read_csv(csv_file, sep=';', index_col=0)
else:
    df_c1 = pd.DataFrame(columns=col)

df_c1 = get_results_1(LINK_C1, df_c1)
print df_c1

df_c1.to_csv('results-c1.csv', sep=';', encoding='utf-8')

# RUGBY - Top14
csv_file = os.path.abspath(os.path.dirname(__file__)) + '/results-top14.csv'
if os.path.isfile(csv_file):
    df_top14 = pd.read_csv(csv_file, sep=';', index_col=0)
else:
    df_top14 = pd.DataFrame(columns=col)

df_top14 = get_results_2(LINK_TOP14, df_top14)

print df_top14
df_top14.to_csv('results-top14.csv', sep=';', encoding='utf-8')


# BASKET - NBA
csv_file = os.path.abspath(os.path.dirname(__file__)) + '/results-nba.csv'
if os.path.isfile(csv_file):
    df_nba = pd.read_csv(csv_file, sep=';', index_col=0)
else:
    df_nba = pd.DataFrame(columns=col)

df_nba = get_results_2(LINK_NBA, df_nba)

print df_nba
df_nba.to_csv('results-nba.csv', sep=';', encoding='utf-8')
