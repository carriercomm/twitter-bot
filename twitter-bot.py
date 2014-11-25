#!/usr/bin/env python

import logging
import tweepy
import sys
import sqlite3
import time
import random
from datetime import datetime

__VERSION__ = '0.1'
__AUTHOR__ = 'smenvis'

CONSUMER_KEY = ''
CONSUMER_SECRET = ''

SLEEP_TIME = 60


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
        '''Parse user input and call correct method'''
        command = raw_input('Enter command (type \'help\' for help): ')
        if command == 'start':
            self.tbot_start()
        elif command == 'setup':
            self.tbot_setup()
        elif command == 'remove':
            self.remove_account()
        elif command == 'help':
            self.tbot_help()
        elif command == 'exit':
            print 'Exiting TwitterBot cleanly.'
            sys.exit()
        else:
            print 'Error: Unknown command.'
            self.cli()

    def tbot_setup(self):
        '''Add Twitter account and keywords etc to database'''
        command = raw_input('Do you want to setup TweetBot (y/n)? ')
        if command == 'n':
            self.cli()
        elif command != 'y':
            print 'Error: You must enter \'y\' for yes or \'n\' no.'
            self.tbot_setup()

        print 'Please enter the following details to configure TweetBot:'

        username = ''
        while len(username) < 1:
            username = raw_input('Username: ')

        access_tokens = self.authorize_twitter_app()

        print 'Seperate Twitter Accounts and Keywords with \',\''

        accounts = ''
        while len(accounts) < 1:
            accounts = raw_input('Enter Twitter Accounts: ')

        keywords = ''
        while len(keywords) < 1:
            keywords = raw_input('Enter Keywords: ')

        conn = sqlite3.connect('twitter-bot.db')
        c = conn.cursor()

        try:
            c.execute('''CREATE TABLE accounts (
                          username text,
                          access_token text,
                          access_token_secret text,
                          twitter_accounts text,
                          keywords text,
                          date text)''')
        except:
            pass

        sql = "INSERT INTO accounts VALUES ('%s', '%s', '%s', '%s', '%s', \
            '%s')" % ( username, access_tokens[0], access_tokens[1], accounts,
            keywords, datetime.now() )

        c.execute(sql)
        conn.commit()

        print 'Success: Twitter Account added to database.'

        # Create database table to store followed twitter account details
        try:
            c.execute('''CREATE TABLE followed_accounts (
                          username text,
                          userid text,
                          keyword text,
                          date text)''')

            print 'Success: Followed Accounts table created.'
        except:
            pass

        conn.close()
        self.cli()

    def authorize_twitter_app(self):
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth_url = auth.get_authorization_url()
        print 'Please authorize: ' + auth_url
        verifier = raw_input('Enter PIN: ').strip()
        auth.get_access_token(verifier)
        #print "ACCESS_KEY = '%s'" % auth.access_token.key
        #print "ACCESS_SECRET = '%s'" % auth.access_token.secret
        return auth.access_token.key, auth.access_token.secret

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
        conn.close()

        print 'Success: %s removed from TwitterBot' % username

        self.cli()

    def tbot_help(self):
        '''TwitterBot help information'''
        print '\ntwitter-bot help information:\n'
        print '\thelp - prints this help information'
        print '\tstart - starts twitter-bot'
        print '\tstats - displays usage stats'
        print '\tsetup - setup twitter-bot'
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
        self.access_token = self.account[1]
        self.access_token_secret = self.account[2]
        self.accounts = self.account[3]
        self.keywords = self.account[4]

        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(auth)

    def main(self):
        '''Pull username for current user and start bot logic'''
        try:
            print 'Starting TweetBot for %s' % self.api.me().screen_name
            print 'Account Stats: Following: %i Followers: %i'  % (
                len(self.api.friends_ids()),
                len(self.api.followers_ids()) )
        except:
            # TODO: Display actual returned error from Twitter
            print 'Error: Unable to pull access Twitter API'
            return

        self.decide_to_follow()
        self.decide_to_unfollow()

    def decide_to_follow(self):
        username = self.pick_random_account()

        print 'Pulling followers for %s' % username
        followers = self.pull_followers(username)

        if followers != 1:
            print '%i followers returned for %s' % (len(followers), username)
        else:
            print 'Error: Unable to pull followers for %s' % username
            return

        # Pick random user from followers
        random_user = random.randrange(0,len(followers)) # -1

        try:
            username = self.api.get_user(followers[random_user]).screen_name
        except:
            print 'Error: Unable to get username from user id'
            return

        print 'Deciding to follow %s' % username

        tweets = self.pull_tweets(username)

        if tweets == 1:
            return

        name_kword = self.parse_tweets(tweets, username)
        if name_kword == False:
            return

        self.follow_user(name_kword[0], followers[random_user], name_kword[1])

    def pick_random_account(self):
        '''Pick random account from accounts in twitter-bot.db'''
        print 'Picking random account'
        usernames = self.accounts.split(",")
        random_user = random.randrange(0,len(usernames)) # -1
        print 'Random account: %s' % usernames[random_user].strip()
        return usernames[random_user].strip()

    def decide_to_unfollow(self):
        print 'Deciding to unfollow random user'
        # Pick random user from database
        conn = sqlite3.connect('twitter-bot.db')
        c = conn.cursor()

        sql = "SELECT * FROM followed_accounts"
        c.execute(sql)

        accounts = c.fetchall()

        random_account = random.randrange(0,len(accounts)) # -1

        print 'Unfollowing user %s' % accounts[random_account][0]

        # TODO: Check date user was followed is >= x
        try:
            self.api.destroy_friendship(accounts[random_account][0])
        except:
            print 'Error: Unable to unfollow user @%s' % accounts[random_account][0]
            conn.close()
            return

        sql = "DELETE FROM followed_accounts WHERE username ='%s'" % accounts[random_account][0]

        c.execute(sql)
        conn.commit()

        conn.close()

    def pull_followers(self, username):
        try:
            return self.api.followers_ids(username)
        except:
            return 1 # TODO: Return actual error

    def follow_user(self, username, userid, keyword):
        conn = sqlite3.connect('twitter-bot.db')
        c = conn.cursor()

        sql = "SELECT * FROM followed_accounts"
        c.execute(sql)

        accounts = c.fetchall()
        print 'Currently %i followed users in database' % len(accounts)


        sql = "SELECT * FROM followed_accounts WHERE username = '%s'" % username
        c.execute(sql)

        if len(c.fetchall()) > 0:
            print '%s has already been followed on %s' % (username, account[3])
            conn.close()
            return

        print 'Checking if %s has already been followed' % username

        print 'Following user %s' % username

        try:
            self.api.create_friendship(userid)
        except:
            print 'Error: Unable to follow user %s' % userid
            conn.close()
            return

        # Add userid, username, keyword and time/date to database
        sql = "INSERT INTO followed_accounts VALUES ('%s', '%s', '%s', '%s')" % (
            username, userid, keyword, datetime.now() )

        c.execute(sql)
        conn.commit()

        conn.close()

    def pull_tweets(self, username):
        print 'Pulling top 500 tweets for %s' % username
        try:
            tweets = self.api.user_timeline(username, count=500)
        except:
            print 'Error: Unable to pull tweets for %s' % username
            return 1
        
        return tweets

    def parse_tweets(self, tweets, username):
        '''Parse tweets for keywords and return user if keyword found'''
        keywords = self.keywords.split(",")
        print 'Parsing %i tweets for %s' % (len(tweets), username)
        for tweet in tweets:
            for word in keywords:
                # TODO: Also check for multi-word keywords in tweets
                # TODO: Convert words to lower before comparing
                if word.strip() in tweet.text.split():
                    print '%s keyword found in tweet' % word.strip()
                    print tweet.text
                    return username, word

        print 'No keywords found in tweets for %s' % username
        return False


if __name__ == '__main__':
    def main():
        twitterbot = TBotInit()
        twitterbot.main()

main()