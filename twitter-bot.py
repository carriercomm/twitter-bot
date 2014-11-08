#!/usr/bin/env python

import logging
import tweepy
import sys

class TwitterBot:
    def main(self):
        print 'Starting TwitterBot...'
        self.cli()

    def cli(self):
        command = raw_input('Enter command (type \'help\' for help): ')
        if command == 'help':
            self.tbot_help()
        elif command == 'exit':
            print 'Exiting TwitterBot cleanly'
            sys.exit()
        else:
            print 'Error: Unknow command'
            self.cli()

    def tbot_help(self):
        print '\ntwitter-bot help information:\n'
        print '\thelp - prints this help information'
        print '\tstart - starts twitter-bot'
        print '\tconfig - config twitter-bot'
        print '\texit = exit twitter-bot\n'
        self.cli()

if __name__ == '__main__':
    def main():
        twitterbot = TwitterBot()
        twitterbot.main()

main()

