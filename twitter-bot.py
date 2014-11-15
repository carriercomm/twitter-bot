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

SLEEP_TIME = 5

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
        command = raw_input('Do you want to setup TweetBot (y/n)? ')
        if command == 'n':
            self.cli()
        elif command != 'y':
            print 'Error: You must enter \'y\' for yes or \'n\' no.'
            self.tbot_config()

        print 'Please enter the following details to configure TweetBot:'

        username = ''
        while username < 1:
            username = raw_input('Username: ')

        access_tokens = self.authorise_twitter_app()

        print 'Seperate Twitter Accounts and Keywords with \',\''

        accounts = ''
        while accounts < 1:
            accounts = raw_input('Enter Twitter Accounts: ')

        keywords = ''
        while keywords < 1:
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
        self.cli()

    def authorise_twitter_app(self):
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

        print 'Success: %s removed from TwitterBot' % username

        self.cli()

    def tbot_help(self):
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
        #self.keywords = self.accounts[4]

        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(self.access_token, self.access_token_secret)

        self.api = tweepy.API(auth)

    def main(self):
        try:
            print 'Starting TweetBot for %s' % self.api.me().screen_name
        except:
            # TODO: Display actual returned error from Twitter
            print 'Error: Unable to pull Twitter username.'
            return

        print 'Picking random account'
        username = self.pick_random_account()

        print 'Pulling followers for %s' % username
        followers = self.pull_followers(username)

        if followers != 1:
            print '%i followers returned for %s' % (len(followers), username)
        else:
            print 'Error: Unable to pull followers for %s' % username
            return

        print 'Deciding to follow random user'
        self.decide_to_follow(followers)

        print 'Deciding to unfollow user'
        self.decide_to_unfollow()

    def pick_random_account(self):
        usernames = self.accounts.split(",")
        random_user = random.randrange(0,len(usernames)) # -1
        print 'Random account: %s' % usernames[random_user].strip()
        return usernames[random_user].strip()

    def decide_to_follow(self, followers):
        # pick random user from followers
        random_user = random.randrange(0,len(followers)) # -1
        print 'Deciding to follow %s' % followers[random_user]

        tweets = self.pull_tweets(followers[random_user])
        if tweets == 1:
            self.decide_to_follow(followers)

        if not self.parse_tweets(followers[random_user]):
            return

        # if so return user
        # if not pick another user
        # favourite tweet
        # follow user
        pass

    def decide_to_unfollow(self):
        # Check date user was followed
        # If user was followed between 1 and two weeks ago (pick random date)
        # - then unfollow
        pass

    def decide_to_favourite(self, tweets):
        pass

    def pull_followers(self, username):
        try:
            return self.api.followers_ids(username)
        except:
            return 1 # TODO: Return actual error

    def pull_following(self, account):
        # Pull users account is following
        # Store in database
        pass

    def follow_user(self, username):
        pass

    def unfollow_user(self, username):
        pass

    def favourite_tweet(self, tweet):
        pass

    def pull_tweets(self, userid):
        print 'Pulling top 100 tweets for %s' % userid
        try:
            tweets = api.user_timeline(userid, count=100)
        except:
            print 'Error: Unable to pull tweets for %s' % userid
            return 1
        
        return tweets

    def parse_tweets(self, tweets):
        # Check if keys words in tweets
        # If so, return True
        # Else return False
        pass


if __name__ == '__main__':
    def main():
        twitterbot = TBotInit()
        twitterbot.main()

main()

