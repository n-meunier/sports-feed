from BeautifulSoup import BeautifulSoup
import re
import os
import urllib2
import pandas as pd
from datetime import datetime, date, timedelta

pattern = r'javascript:pop.*,\'(.*)-vs-(.*)\/(\d{2}-\d{2}-\d{4})\''
col = ['date', 'team-home', 'team-away', 'score-home', 'score-away']
LINK_LIGUE1 = 'link'
LINK_TOP14 = 'link'
LINK_NBA = 'link'
LINK_C1 = 'link'

yesterday = date.today() - timedelta(4)
yesterday_format = yesterday.strftime('%a %d %b %Y')
y_df_format = yesterday.strftime('%d-%m-%Y')

# FOOT - Ligue 1
csv_file = os.path.abspath(os.path.dirname(__file__)) + '/results-ligue1.csv'
if os.path.isfile(csv_file):
    df_ligue1 = pd.read_csv(csv_file, sep=';', index_col=0)
else:
    df_ligue1 = pd.DataFrame(columns=col)

page = urllib2.urlopen(LINK_LIGUE1).read()
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
                        df_ligue1 = df_ligue1.append({'date': date,
                                                      'team-home': hteam,
                                                      'team-away': ateam,
                                                      'score-home': hscore,
                                                      'score-away': ascore},
                                                     ignore_index=True)
    except AttributeError as error:
        print('No data for %s' % str(date))
        print(error)

# for p in soup.findAll('a'):
#     if p.get('title'):
#         if 'Match Details' in p.get('title'):
#             m = re.match(pattern, p.get('href'))
#             m_score = re.match('(\d) - (\d)', p.text)
#             df_ligue1 = df_ligue1.append({'date': m.group(3),
#                                           'team-home': m.group(1),
#                                           'team-away': m.group(2),
#                                           'score-home': m_score.group(1),
#                                           'score-away': m_score.group(2)},
#                                          ignore_index=True)
            # print p.text
df_ligue1 = df_ligue1.drop_duplicates(['date', 'team-home']).reset_index(drop=True)

print df_ligue1

df_ligue1.to_csv('results-ligue1.csv', sep=';', encoding='utf-8')

# FOOT - Champions League
csv_file = os.path.abspath(os.path.dirname(__file__)) + '/results-c1.csv'
if os.path.isfile(csv_file):
    df_c1 = pd.read_csv(csv_file, sep=';', index_col=0)
else:
    df_c1 = pd.DataFrame(columns=col)
page = urllib2.urlopen(LINK_C1).read()
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
                        df_c1 = df_c1.append({'date': date,
                                              'team-home': hteam,
                                              'team-away': ateam,
                                              'score-home': hscore,
                                              'score-away': ascore},
                                             ignore_index=True)
    except AttributeError as error:
        print('No data for %s' % str(date))
        print(error)

# for p in soup.findAll('a'):
#     if p.get('title'):
#         if 'Match Details' in p.get('title'):
#             m = re.match(pattern, p.get('href'))
#             m_score = re.match('(\d) - (\d)', p.text)
#             df_ligue1 = df_ligue1.append({'date': m.group(3),
#                                           'team-home': m.group(1),
#                                           'team-away': m.group(2),
#                                           'score-home': m_score.group(1),
#                                           'score-away': m_score.group(2)},
#                                          ignore_index=True)
            # print p.text
df_c1 = df_c1.drop_duplicates(['date', 'team-home']).reset_index(drop=True)

print df_c1

df_c1.to_csv('results-c1.csv', sep=';', encoding='utf-8')

# RUGBY - Top14
csv_file = os.path.abspath(os.path.dirname(__file__)) + '/results-top14.csv'
if os.path.isfile(csv_file):
    df_rugby = pd.read_csv(csv_file, sep=';', index_col=0)
else:
    df_rugby = pd.DataFrame(columns=col)
# df_rugby = pd.DataFrame(columns=col)
page = urllib2.urlopen(LINK_TOP14).read()
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
                        df_rugby = df_rugby.append({'date': date,
                                                    'team-home': hteam,
                                                    'team-away': ateam,
                                                    'score-home': hscore,
                                                    'score-away': ascore},
                                                   ignore_index=True)
    except AttributeError as error:
        print('No data for %s' % str(date))
        print(error)

df_rugby = df_rugby.drop_duplicates(['date', 'team-home']).reset_index(drop=True)
print df_rugby
df_rugby.to_csv('results-top14.csv', sep=';', encoding='utf-8')


# BASKET - NBA
csv_file = os.path.abspath(os.path.dirname(__file__)) + '/results-nba.csv'
if os.path.isfile(csv_file):
    df_basket = pd.read_csv(csv_file, sep=';', index_col=0)
else:
    df_basket = pd.DataFrame(columns=col)
page = urllib2.urlopen(LINK_NBA).read()
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
                        df_basket = df_basket.append({'date': date,
                                                      'team-home': hteam,
                                                      'team-away': ateam,
                                                      'score-home': hscore,
                                                      'score-away': ascore},
                                                     ignore_index=True)
    except AttributeError as error:
        print('No data for %s' % str(date))
        print(error)

df_basket = df_basket.drop_duplicates(['date', 'team-home']).reset_index(drop=True)
print df_basket
df_basket.to_csv('results-nba.csv', sep=';', encoding='utf-8')

# page = urllib2.urlopen('https://www.scorespro.com/rugby-union/france/top-14/results/').read()
# soup = BeautifulSoup(page)
#
# for p in soup.findAll('li'):
#     if 'Sun' in p.text:
#         print p
# datetime.strftime(datetime.now() - timedelta(1), '%d-%m-%Y')
