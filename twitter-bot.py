#!/usr/bin/env python

import logging
import tweepy
import sys
import sqlite3
import time
from datetime import datetime

__VERSION__ = '0.1'
__AUTHOR__ = 'smenvis'

SLEEP_TIME = 15

class TBotInit:
    def main(self):
        print """

           88888                         w   888b.        w   
             8   Yb  db  dP .d88b .d88b w8ww 8wwwP .d8b. w8ww 
             8    YbdPYbdP  8.dP' 8.dP'  8   8   b 8' .8  8   
             8     YP  YP   `Y88P `Y88P  Y8P 888P' `Y8P'  Y8P

                             TweetBot - v%s
        """  % __VERSION__

        self.cli()

    def cli(self):
        command = raw_input('Enter command (type \'help\' for help): ')
        if command == 'help':
            self.tbot_help()
        elif command == 'start':
            self.tbot_start()
        elif command == 'config':
            self.tbot_config()
        elif command == 'remove':
            self.remove_account()
        elif command == 'exit':
            print 'Exiting TwitterBot cleanly.'
            sys.exit()
        else:
            print 'Error: Unknown command.'
            self.cli()

    def tbot_config(self):
        command = raw_input('Do you want to setup TweetBot (y/n)? ')
        if command == 'n':
            self.cli()
        elif command != 'y':
            print 'Error: You must enter \'y\' for yes or \'n\' no.'
            self.tbot_config()

        print 'Please enter the following details to configure TweetBot:'
        # TODO: Add error correction to ensure user enters values
        username = raw_input('Username: ')
        consumer_key = raw_input('Consumer Key: ')
        consumer_secret = raw_input('Consumer Secret: ')
        access_token = raw_input('Access Token: ')
        access_token_secret = raw_input('Access Token Secret: ')
        print 'Seperate Twitter Accounts and Keywords with \',\''
        accounts = raw_input('Enter Twitter Accounts: ')
        keywords = raw_input('Enter Keywords: ')

        conn = sqlite3.connect('twitter-bot.db')
        c = conn.cursor()

        try:
            c.execute('''CREATE TABLE accounts (
                          username text,
                          consumer_key text,
                          consumer_secret text,
                          access_token text,
                          access_token_secret text,
                          twitter_accounts text,
                          keywords text,
                          date text)''')
        except:
            pass

        sql = "INSERT INTO accounts VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % ( username, consumer_key, consumer_secret, access_token, access_token_secret, accounts, keywords, datetime.now() )

        c.execute(sql)
        conn.commit()

        print 'Success: Twitter Account added to database.'
        self.cli()

    def remove_account(self):
        username = ''
        while len(username) < 1:
            username = raw_input('Enter username of account to remove: ')

        conn = sqlite3.connect('twitter-bot.db')
        c = conn.cursor()

        sql = "SELECT * FROM accounts WHERE username = '%s'" % username
        c.execute(sql)

        account = c.fetchall()

        if len(account) == 0:
            print 'Error: Account with username \'%s\' not found' % username
            self.cli()

        sql = "DELETE FROM accounts WHERE username ='%s'" % username

        c.execute(sql)
        conn.commit()

        print 'Success: %s removed from TwitterBot' % username

        self.cli()

    def tbot_help(self):
        print '\ntwitter-bot help information:\n'
        print '\thelp - prints this help information'
        print '\tstart - starts twitter-bot'
        print '\tstats - displays usage stats'
        print '\tconfig - config twitter-bot'
        print '\tremove - remove Twitter account'
        print '\texit - exit twitter-bot\n'
        self.cli()

    def tbot_start(self):
        print 'Starting TwitterBot...'

        conn = sqlite3.connect('twitter-bot.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM accounts")
        accounts = cur.fetchall()

        while 1:
            for account in accounts:
                TweetBot(account).main()
                print 'Sleeping for %i seconds...' % SLEEP_TIME
                time.sleep(SLEEP_TIME)


class TweetBot:
    def __init__(self, account):
        self.account = account
        self.username = self.account[0]
        self.consumer_key = self.account[1]
        self.consumer_secret = self.account[2]
        self.access_token = self.account[3]
        self.access_token_secret = self.account[4]
        self.accounts = self.account[5]
        self.keywords = self.accounts[6]

    def main(self):
        print 'Starting TweetBot for %s' % self.username
        # self.pull_followers(account)
        # self.pull_following(account)
        pass

    def decide_to_follow(self, username, tweets):
        pass

    def decide_to_unfollow(self, username):
        # check date user was followed
        # if user was followed between 1 and two weeks ago (pick random date) unfollow
        pass

    def decide_to_favourite(self, tweets):
        pass

    def pull_followers(self, account):
        # pull users following account
        # store in database
        pass

    def pull_following(self, account):
        # pull users account is following
        # store in database
        pass

    def follow_user(self, username):
        pass

    def unfollow_user(self, username):
        pass

    def favourite_tweet(self, tweet):
        pass

    def pull_tweets(self, username):
        pass

    def parse_tweets(self, keywords, tweets):
        pass


if __name__ == '__main__':
    def main():
        twitterbot = TBotInit()
        twitterbot.main()

main()

