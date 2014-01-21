#!/usr/local/bin/python2.7

# Shut That Down

""" Shut That Down is a collection of quotes of hate speech by public figures 
    Shut That Down aims to connect the dots between the donors, funders, and advertisers bankrolling everyday hate speech
"""

import cherrypy                             # pip install cherrypy      or download at http://cherrypy.org/
from crpapi import CRP, CRPApiError         # Download at: http://www.opensecrets.org/resources/create/apis.php
import json
import psycopg2                             # pip install psycopg2      or download at: https://pypi.python.org/pypi/psycopg2
import random
import shutthatdown_.shutthatdown_credentials as shutthatdown_credentials # Edit this file with your API keys and database credentials
import urllib
import urllib2

class Root(object):

    import shutthatdown_.shutthatdown_index

    import shutthatdown_.shutthatdown_about
    import shutthatdown_.shutthatdown_browse_persons
    import shutthatdown_.shutthatdown_browse_quotes
    import shutthatdown_.shutthatdown_enablers
    import shutthatdown_.shutthatdown_error_page
    import shutthatdown_.shutthatdown_inmystate
    import shutthatdown_.shutthatdown_quote
    import shutthatdown_.shutthatdown_random_quote
    import shutthatdown_.shutthatdown_search
    import shutthatdown_.shutthatdown_special_thanks
    import shutthatdown_.shutthatdown_stats
    import shutthatdown_.shutthatdown_submit_quote
    import shutthatdown_.shutthatdown_welove
             
    index = shutthatdown_.shutthatdown_index.index

    about = shutthatdown_.shutthatdown_about.about
    browse_persons = shutthatdown_.shutthatdown_browse_persons.browse_persons
    browse_quotes = shutthatdown_.shutthatdown_browse_quotes.browse_quotes
    enablers = shutthatdown_.shutthatdown_enablers.enablers
    error_page = shutthatdown_.shutthatdown_error_page.error_page
    inmystate = shutthatdown_.shutthatdown_inmystate.inmystate
    quote = shutthatdown_.shutthatdown_quote.quote
    random_quote = shutthatdown_.shutthatdown_random_quote.random_quote
    search = shutthatdown_.shutthatdown_search.search
    special_thanks = shutthatdown_.shutthatdown_special_thanks.special_thanks
    stats = shutthatdown_.shutthatdown_stats.stats
    submit_quote = shutthatdown_.shutthatdown_submit_quote.submit_quote
    welove = shutthatdown_.shutthatdown_welove.welove

    index.exposed = True

    about.exposed = True
    browse_persons.exposed = True
    browse_quotes.exposed = True
    enablers.exposed = True
    error_page.exposed = True
    inmystate.exposed = True
    quote.exposed = True
    random_quote.exposed = True
    search.exposed = True
    special_thanks.exposed = True
    stats.exposed = True
    submit_quote.exposed = True
    welove.exposed = True

if __name__ == "__main__":

    import os.path
    current_dir = os.path.dirname(os.path.abspath(__file__))

    cherrypy.root = Root()

    cherrypy.config.update({'server.socket_port': 8080,
                            'server.socket_host': '127.0.0.1',
                            'log.screen': True,
                            'log.error_file': 'site.log',
                            'server.environment': 'production',
                            'error_page.default': cherrypy.root.error_page,
                            })

    conf = {'/favicon.png': {'tools.staticfile.on': True,
                            'tools.staticfile.filename': os.path.join(current_dir, 'favicon.png')},
            '/icons': {'tools.staticdir.on': True,
                      'tools.staticdir.dir': os.path.join(current_dir, 'icons'),},
            '/css': {'tools.staticdir.on': True,
                      'tools.staticdir.dir': os.path.join(current_dir, 'css'),},
            '/js': {'tools.staticdir.on': True,
                      'tools.staticdir.dir': os.path.join(current_dir, 'js'),},
            }
    
    cherrypy.quickstart(cherrypy.root, '/', config=conf)
