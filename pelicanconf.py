#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
from datetime import date

AUTHOR = 'Ben Anhalt'
SITENAME = 'con.cor.dance'
SITEURL = ''
THEME = './Flex'
SITETITLE = 'con.cor.dance'
SITESUBTITLE = 'the state of being in harmony'
#SITEDESCRIPTION = 'Foo Bar\'s Thoughts and Writings'
SITELOGO = SITEURL + '/images/profile.jpg'
FAVICON = SITEURL + '/images/favicon.ico'

BROWSER_COLOR = '#333'
ROBOTS = 'index, follow'

CC_LICENSE = {
    'name': 'Creative Commons Attribution-ShareAlike',
    'version': '4.0',
    'slug': 'by-sa'
}

COPYRIGHT_YEAR = date.today().year
MAIN_MENU = True

PATH = 'content'

TIMEZONE = 'US/Central'

DEFAULT_LANG = 'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
