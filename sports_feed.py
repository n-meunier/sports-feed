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
0.9.0     2018/10/04     Added: Get the round. Changed: Merge all the output
                         into one csv. Merge the functions to get results and
                         fixtures into one.
0.10.0    2018/10/05     Added: Get the results from web only if passed games
                         have no result or there is no game from today
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
__date__ = '2018/10/05'
__version__ = '0.10.0'

# [GLOBALS]--------------------------------------------------------------------
TODAY = (date.today()).strftime('%Y-%m-%d')
pattern = r'javascript:pop.*,\'(.*)-vs-(.*)\/(\d{2}-\d{2}-\d{4})\''
# col = ['date', 'team-home', 'team-away', 'score-home', 'score-away']
col = ['date', 'time', 'status', 'team-home', 'team-away', 'score-home',
       'score-away', 'round', 'sport', 'league']


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


def get_games(link, df, sport, league, results=True):
    """ Return a dataframe with the game results on from a link with data in
    format 1.
    :param link: url to the website
    :param df: Dataframe to fill
    :return: updated dataframe
    """
    # link = link + 'results/'
    # page = urllib2.urlopen(link).read()
    # soup = BeautifulSoup(page)
    if results:
        soup = get_data(link, 'results')
    else:
        soup = get_data(link, 'fixtures')

    if not soup:
        return False

    # For all div
    for ncet in soup.findAll('div'):
        # Get only the 'ncet' div
        if ncet.get('class') and 'ncet' in ncet.get('class'):
            round_number = ''
            game_date = ''
            game_time = ''
            # Get the round and date if available
            for t in ncet.findAll('li'):
                if t.get('class') and 'round' in t.get('class'):
                    match = re.match('(Round|Matchday) (\d+)', t.text)
                    if match:
                        round_number = match.group(2)
                    else:
                        round_number = t.text
                if t.get('class') and 'date' in t.get('class'):
                    game_date = datetime.strptime(t.text, '%a %d %b %Y').strftime('%Y-%m-%d')

            try:
                # Games data are in the div after round and date
                div = t.findNext('div')
                for table in div.findAll('table'):
                    hteam = ''
                    ateam = ''
                    hscore = ''
                    ascore = ''
                    status = ''
                    # One game per 1 or 2 table row
                    for team in table.findAll('tr'):
                        # For each table cell, find the corresponding data
                        for q in team.findAll('td'):
                            if q.get('class') and 'datetime' in q.get('class'):
                                game_time = q.text
                            if q.get('class') and 'kick_t' in q.get('class'):
                                for span in q.findAll('span'):
                                    if span.get('class') and 'dt' in \
                                            span.get('class'):
                                        game_date = datetime.strptime(span.text,
                                                                      '%d.%m.%y').strftime('%Y-%m-%d')
                                    elif span.get('class') and 'ko' in \
                                            span.get('class'):
                                        game_time = span.text
                            if q.get('class') and 'status' in q.get('class'):
                                status = q.text
                            if q.get('class') and 'home' in q.get('class'):
                                hteam = q.text
                                if ';' in hteam:
                                    hteam = hteam.split(';', 1)[1]
                            if q.get('class') and 'away' in q.get('class'):
                                ateam = q.text
                                if ';' in ateam:
                                    ateam = ateam.split(';', 1)[1]
                            if q.get('class') and 'score' in q.get('class'):
                                score = re.match('(\d+) - (\d+)', q.text)
                                if score:
                                    hscore = score.group(1)
                                    ascore = score.group(2)
                            if q.get('class') and 'setB' in q.get('class') \
                                    and not hscore:
                                hscore = q.text
                                if ';' in hscore:
                                    hscore = hscore.split(';', 1)[1]
                        # If away team was not found in the row, must be a 2
                        # rows game
                        if not ateam:
                            away_team = team.findNext('tr')
                            for q in away_team.findAll('td'):
                                if q.get('class') and 'away' in q.get('class'):
                                    ateam = q.text
                                    if ';' in ateam:
                                        ateam = ateam.split(';', 1)[1]
                                if q.get('class') and 'setB' in q.get('class'):
                                    ascore = q.text
                                    if ';' in ascore:
                                        ascore = ascore.split(';', 1)[1]
                    # print('[%s %s] Round %s: (%s) %s %s - %s %s' %
                    #       (game_date, game_time, round_number, status, hteam,
                    #        hscore, ascore, ateam))

                    # Append to the dataframe
                    df = df.append({'date': game_date,
                                    'time': game_time,
                                    'status': status,
                                    'team-home': hteam,
                                    'team-away': ateam,
                                    'score-home': hscore,
                                    'score-away': ascore,
                                    'round': round_number,
                                    'sport': sport,
                                    'league': league},
                                   ignore_index=True)
            except AttributeError as error:
                print('No data for %s' % str(game_date))
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
                        help='League targeted (must be defined in the config '
                             'file). Ex:'
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

    csv_file = os.path.abspath(os.path.dirname(__file__)) + '/results.csv'
    if os.path.isfile(csv_file):
        df = pd.read_csv(csv_file, sep=';', index_col=0)
    else:
        df = pd.DataFrame(columns=col)

    # print leagues
    for league in leagues:
        print('\n' + leagues[league]['name'] + ':')

        df_league = df.loc[df['league'] == leagues[league]['name']]

        # Get data from the web initialized to False
        check_needed = False
        df_test = df_league.loc[df['date'] < TODAY]

        # if league is not in the dataframe OR previous games are not \
        #         up-to-date OR there is no games from today
        if len(df_league) < 1 or len(df_league.loc[df['date'] >= TODAY]) < 1 or\
                (df_league.loc[df['date'] < TODAY])['status'].isnull().values.any():
            check_needed = True

        # if there is games but no results, get the results
        if check_needed:
            print('Get the results...')
            df = get_games(leagues[league]['link'], df,
                           leagues[league]['sport'], leagues[league]['name'],
                           results=True)
            df = get_games(leagues[league]['link'], df,
                           leagues[league]['sport'], leagues[league]['name'],
                           results=False)
            df_sort = df.sort_values(by=['status'])
            df = df_sort.drop_duplicates(['date', 'team-home'],
                                         keep='first').reset_index(drop=True)
            # df.to_csv(leagues[league]['output'], sep=';', encoding='utf-8')

        # if the optional date is provided
        if check_date:
            df_request = df.loc[df['date'] == check_date]
        else:
            today = (date.today()).strftime('%Y-%m-%d')
            df_request = df.loc[df['date'] < today]
        df_request = df_request.loc[df['league'] == leagues[league]['name']]

        print('%s:' % check_date)
        if len(df_request.index) > 0:
            print(df_request)
        else:
            print('No results found')

    df.to_csv('results.csv', sep=';', encoding='utf-8')


if __name__ == '__main__':
    main()
