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
__date__ = '2018/09/10'
__version__ = '0.6.0'

# [GLOBALS]--------------------------------------------------------------------
pattern = r'javascript:pop.*,\'(.*)-vs-(.*)\/(\d{2}-\d{2}-\d{4})\''
col = ['date', 'team-home', 'team-away', 'score-home', 'score-away']

yesterday = date.today() - timedelta(1)
yesterday_format = yesterday.strftime('%a %d %b %Y')
y_df_format = yesterday.strftime('%Y-%m-%d')


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

    # df = df.drop_duplicates(['date', 'team-home']).reset_index(drop=True)
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
        date = datetime.strptime(t, '%a %d %b %Y').strftime('%Y-%m-%d')

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
    # df = df.drop_duplicates(['date', 'team-home']).reset_index(drop=True)
    return df


# [MAIN] ----------------------------------------------------------------------
def main():
    """Main function"""

    # Parse command line argument
    aadhf = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description="Get sports results from the "
                                                 "web.",
                                     formatter_class=aadhf)

    parser.add_argument('-l', '--leagues', dest='leagues', default='all',
                        help='Sports leagues targeted:'
                             '- l1: Ligue 1 (football)'
                             '- c1: UEFA Champions League (football)'
                             '- nl: UEFA Nations League (football)'
                             '- top14: Top 14 (rugby)'
                             '- nba: NBA (basketball)'
                             '- all: All leagues above (default)')
    parser.add_argument('-y', '--yesterday', action='store_true',
                        help='Show only yesterday\'s results')

    args = parser.parse_args()

    if args.yesterday:
        yesterday_only = True
    else:
        yesterday_only = False

    all_leagues = read_leagues_info()

    # Get the leagues to check
    if args.leagues in all_leagues:
        leagues = {args.leagues: all_leagues[args.leagues]}
    elif args.leagues == 'all':
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

        if leagues[league]['format'] == 1:
            df = get_results_1(leagues[league]['link'], df)
        elif leagues[league]['format'] == 2:
            df = get_results_2(leagues[league]['link'], df)
        df = df.sort_values(by=['date']).drop_duplicates(['date',
                                                          'team-home']).reset_index(drop=True)
        if yesterday_only:
            print('Yesterday:')
            df_yesterday = df.loc[df['date'] == y_df_format]
            if len(df_yesterday.index) > 0:
                print(df_yesterday)
            else:
                print('No results found')
        else:
            if len(df.index) > 0:
                print df
            else:
                print('No results found')
        df.to_csv(leagues[league]['output'], sep=';', encoding='utf-8')

    # FOOT - Ligue 1
    # csv_file = os.path.abspath(os.path.dirname(__file__)) + '/' + \
    #            LEAGUES_LIST['l1']['output']
    # print csv_file
    # if os.path.isfile(csv_file):
    #     df_ligue1 = pd.read_csv(csv_file, sep=';', index_col=0)
    # else:
    #     df_ligue1 = pd.DataFrame(columns=col)
    #
    # df_ligue1 = get_results_1(LINK_LIGUE1, df_ligue1)
    # print df_ligue1
    #
    # df_ligue1.to_csv('results-ligue1.csv', sep=';', encoding='utf-8')
    #
    # # FOOT - Champions League
    # csv_file = os.path.abspath(os.path.dirname(__file__)) + '/results-c1.csv'
    # if os.path.isfile(csv_file):
    #     df_c1 = pd.read_csv(csv_file, sep=';', index_col=0)
    # else:
    #     df_c1 = pd.DataFrame(columns=col)
    #
    # df_c1 = get_results_1(LINK_C1, df_c1)
    # print df_c1
    #
    # df_c1.to_csv('results-c1.csv', sep=';', encoding='utf-8')
    #
    # # FOOT - Nations League
    # csv_file = os.path.abspath(os.path.dirname(__file__)) + '/results-nl.csv'
    # if os.path.isfile(csv_file):
    #     df_nl = pd.read_csv(csv_file, sep=';', index_col=0)
    # else:
    #     df_nl = pd.DataFrame(columns=col)
    #
    # df_nl = get_results_1(LINK_NL, df_nl)
    # print df_nl
    #
    # df_nl.to_csv('results-nl.csv', sep=';', encoding='utf-8')
    #
    # # RUGBY - Top14
    # csv_file = os.path.abspath(os.path.dirname(__file__)) + '/results-top14.csv'
    # if os.path.isfile(csv_file):
    #     df_top14 = pd.read_csv(csv_file, sep=';', index_col=0)
    # else:
    #     df_top14 = pd.DataFrame(columns=col)
    #
    # df_top14 = get_results_2(LINK_TOP14, df_top14)
    #
    # print df_top14
    # df_top14.to_csv('results-top14.csv', sep=';', encoding='utf-8')
    #
    #
    # # BASKET - NBA
    # csv_file = os.path.abspath(os.path.dirname(__file__)) + '/results-nba.csv'
    # if os.path.isfile(csv_file):
    #     df_nba = pd.read_csv(csv_file, sep=';', index_col=0)
    # else:
    #     df_nba = pd.DataFrame(columns=col)
    #
    # df_nba = get_results_2(LINK_NBA, df_nba)
    #
    # print df_nba
    # df_nba.to_csv('results-nba.csv', sep=';', encoding='utf-8')


if __name__ == '__main__':
    main()
