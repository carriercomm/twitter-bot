twitter-bot
===========

Simple Twitter Bot written in Python

A simple Twitter bot, using the Tweepy module, that follows specific
accounts in the hope that they will follow back. The user sets a list
of Twitter accounts where users to follow should be selected from.

Tweets from those accounts are then checked to see if they contain any
pre-selected key-words, if they do that user is followed.

Any users that do not follow back within a set amount of time are un-
followed. Users that do follow back are also un-followed after a pre-set
amount of time.

twitter-bot will also favourite a tweet from newly followed users that
contain a pre-selected key-word. If more than one tweet contains the
key-word then the most recent tweet to contain that key-word is
favourited.

smenvis
