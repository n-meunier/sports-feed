#!/usr/bin/env python
# coding: utf8
# =============================================================================
#            Nicolas Meunier
# =============================================================================
# PROJECT : Sports results feeder
# FILE : sports_feed.py
# DESCRIPTION :
"""
    From specific websites, get sports results on leagues selected from a
    configuration file.

Use: python sports_feed.py -l [LEAGUE]

Requirements:
- BeautifulSoup
- pandas

========= ============== ======================================================
Version   Date           Comment
========= ============== ======================================================
0.1.0     2018/09/05     Initial version
0.2.0     2018/09/05     Updated: Factorize in functions
0.3.0     2018/09/07     Added: Read leagues info from config file. Optional
                         argument to select the league.
0.4.0     2018/09/07     Changed: Read leagues info from json file.
0.6.0     2018/09/10     Added: Optional argument to only display the
                         previous day
0.7.0     2018/09/16     Added: Get the future schedule from another link
0.8.0     2018/09/17     Changed: Optional argument to only display one day
                         (before or after)
                         Added: Get the data from the web only if the results
                         are not available locally
========= ============== ======================================================
"""

# [IMPORTS]--------------------------------------------------------------------
try:
    from BeautifulSoup import BeautifulSoup
except:
    from bs4 import BeautifulSoup
import re
import os
import urllib2
import pandas as pd
from datetime import datetime, date, timedelta
import ConfigParser, argparse
import json

# [MODULE INFO]----------------------------------------------------------------
__author__ = 'nmeunier'
__date__ = '2018/09/17'
__version__ = '0.8.0'

# [GLOBALS]--------------------------------------------------------------------
pattern = r'javascript:pop.*,\'(.*)-vs-(.*)\/(\d{2}-\d{2}-\d{4})\''
col = ['date', 'team-home', 'team-away', 'score-home', 'score-away']


# [FUNCTIONS] -----------------------------------------------------------------
def read_leagues_info():
    """Read a config file to get the link, the output path and the html
    format for each league.
    :return: dictionary of leagues.
    """
    leagues = {}

    config = ConfigParser.ConfigParser()
    config.read('sports_config.cfg')

    with open('sports-config.json') as f:
        leagues = json.load(f)

    return leagues


def get_data(link, type):
    """ Get the html data from the weblink and return a soup.
    :param link: link to the league data
    :param type: End of link to get the future schedule or the past results
    :return: BeautifulSoup html page
    """
    if type == 'results' or type == 'fixtures':
        link = link + type
        page = urllib2.urlopen(link).read()
        return BeautifulSoup(page)
    else:
        return False


def get_results_1(link, df):
    """ Return a dataframe with the game results on from a link with data in
    format 1.
    :param link: url to the website
    :param df: Dataframe to fill
    :return: updated dataframe
    """
    # link = link + 'results/'
    # page = urllib2.urlopen(link).read()
    # soup = BeautifulSoup(page)

    soup = get_data(link, 'results')

    if not soup:
        return False

    for t in soup.findAll('p', text=re.compile("(\w{3} \d{2} \w{3} \d{4})")):
        date = datetime.strptime(t, '%a %d %b %Y').strftime('%Y-%m-%d')
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

    return df


def get_schedule_1(link, df):
    """ Return a dataframe with the game results on from a link with data in
    format 1.
    :param link: url to the website
    :param df: Dataframe to fill
    :return: updated dataframe
    """
    soup = get_data(link, 'fixtures')

    if not soup:
        return False

    for t in soup.findAll('p', text=re.compile("(\w{3} \d{2} \w{3} \d{4})")):
        date = datetime.strptime(t, '%a %d %b %Y').strftime('%Y-%m-%d')
        # print date

        try:
            div = t.findNext('div')
            for table in div.findAll('table'):
                for p in table.findAll('span'):
                    if p.get('title'):
                        hteam = ''
                        ateam = ''
                        hscore = ''
                        ascore = ''
                        game = p.findParent('tr')
                        for q in game.findAll('td'):
                            # print q
                            if q.get('class') and 'home' in q.get('class'):
                                hteam = q.text
                                # print('team-home: %s' % hteam)
                            if q.get('class') and 'away' in q.get('class'):
                                ateam = q.text
                                # print('team-away: %s' % ateam)
                        df = df.append({'date': date,
                                        'team-home': hteam,
                                        'team-away': ateam,
                                        'score-home': hscore,
                                        'score-away': ascore},
                                       ignore_index=True)
        except AttributeError as error:
            print('No data for %s' % str(date))
            print(error)

    return df


def get_results_2(link, df):
    """ Return a dataframe with the game results on from a link with data in
    format 2.
    :param link: url to the website
    :param df: Dataframe to fill
    :return: updated dataframe
    """
    soup = get_data(link, 'results')

    if not soup:
        return False

    for t in soup.findAll('p', text=re.compile("(\w{3} \d{2} \w{3} \d{4})")):
        date = datetime.strptime(t, '%a %d %b %Y').strftime('%Y-%m-%d')

        try:
            # div = foundtext.findNext('div')
            div = t.findNext('div')
            # table = foundtext.findNext('table')
            for table in div.findAll('table'):
                for p in table.findAll('span'):
                    if p.get('title'):
                        if 'AOT' in p.text or 'FT' in p.text:
                            # time = p.text
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

    return df


def get_schedule_2(link, df):
    """ Return a dataframe with the game schedule from a link with data in
    format 2.
    :param link: url to the website
    :param df: Dataframe to fill
    :return: updated dataframe
    """
    soup = get_data(link, 'fixtures')

    if not soup:
        return False

    for t in soup.findAll('p', text=re.compile("(\w{3} \d{2} \w{3} \d{4})")):
        # print t
        date = datetime.strptime(t, '%a %d %b %Y').strftime('%Y-%m-%d')

        try:
            # div = foundtext.findNext('div')
            div = t.findNext('div')
            # print div
            # table = foundtext.findNext('table')
            for table in div.findAll('table'):
                # print table
                # print 'GAME'
                hteam = ''
                ateam = ''
                hscore = ''
                ascore = ''
                for team in table.findAll('tr'):
                    # print 'TEAM 1'
                    # print team
                    for q in team.findAll('td'):
                        # print q
                        if q.get('class') and 'hometeam' in q.get('class'):
                            hteam = (re.match('.*;(.*)', q.text)).group(1)
                            # print('team-home: %s' % hteam)
                            # print('score-home: %s' % hscore)
                        if q.get('class') and 'awayteam' in q.get('class'):
                            ateam = (re.match('.*;(.*)', q.text)).group(1)
                            # print('team-away: %s' % ateam)
                df = df.append({'date': date,
                                'team-home': hteam,
                                'team-away': ateam,
                                'score-home': hscore,
                                'score-away': ascore},
                               ignore_index=True)
        except AttributeError as error:
            print('No data for %s' % str(date))
            print(error)

    return df


# [MAIN] ----------------------------------------------------------------------
def main():
    """Main function"""

    # Parse command line argument
    aadhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description="Get sports results from the "
                                                 "web.",
                                     formatter_class=aadhf)

    parser.add_argument('-l', '--league', dest='league', default='all',
                        help='League targeted:'
                             '- l1: Ligue 1 (football)'
                             '- c1: UEFA Champions League (football)'
                             '- nl: UEFA Nations League (football)'
                             '- top14: Top 14 (rugby)'
                             '- nba: NBA (basketball)'
                             '- all: All leagues above (default)')
    parser.add_argument('-d', '--date', dest='date', default=None,
                        help='Show only results for the day given (format '
                             'YYYY-mm-dd, ex: 2018-09-17). Default is all the '
                             'dates until yesterday.'
                             'Possibility to give \'yesterday\', \'today\' or '
                             '\'tomorrow\'.'
                             'If the date is today or later, give the schedule.')

    args = parser.parse_args()

    if args.date:
        if args.date == 'yesterday':
            check_date = (date.today() - timedelta(1)).strftime('%Y-%m-%d')
        elif args.date == 'today':
            check_date = (date.today()).strftime('%Y-%m-%d')
        elif args.date == 'tomorrow':
            check_date = (date.today() + timedelta(1)).strftime('%Y-%m-%d')
        else:
            m = re.match('(\d{4}-\d{2}-\d{2})', args.date)
            if m:
                check_date = m.group(1)
            else:
                print('Cannot read the date, fallback to default value: all.')
                check_date = None
    else:
        print('No date, will show all the previous results.')
        check_date = None

    all_leagues = read_leagues_info()

    # Get the leagues to check
    if args.league in all_leagues:
        leagues = {args.league: all_leagues[args.league]}
    elif args.league == 'all':
        print('All the leagues will be checked.')
        leagues = all_leagues
    else:
        print('The league you are asking is not available. Fallback to the '
              'default ones.')
        leagues = all_leagues

    # print leagues
    for league in leagues:
        print('\n' + leagues[league]['name'] + ':')
        csv_file = os.path.abspath(os.path.dirname(__file__)) + '/' + \
                   leagues[league]['output']
        if os.path.isfile(csv_file):
            df = pd.read_csv(csv_file, sep=';', index_col=0)
        else:
            df = pd.DataFrame(columns=col)

        if check_date:
            df_date = df.loc[df['date'] == check_date]
        else:
            df_date = df.loc[df['date'] < (date.today()).strftime('%Y-%m-%d')]

        # if there is games but no results, get the results
        if df_date.isnull().values.any() or len(df_date.index) < 1:
            print('Get the results...')
            if leagues[league]['format'] == 1:
                df = get_results_1(leagues[league]['link'], df)
                df = get_schedule_1(leagues[league]['link'], df)
            elif leagues[league]['format'] == 2:
                df = get_results_2(leagues[league]['link'], df)
                df = get_schedule_2(leagues[league]['link'], df)
            df = df.sort_values(by=['date']).drop_duplicates(['date',
                                                              'team-home']).reset_index(drop=True)
            df.to_csv(leagues[league]['output'], sep=';', encoding='utf-8')
            df_date = df.loc[df['date'] == check_date]

        print('%s:' % check_date)
        if len(df_date.index) > 0:
            print(df_date)
        else:
            print('No results found')


if __name__ == '__main__':
    main()
