#!/usr/local/bin/python2.7

import cherrypy

class Root(object):


    from shutthatdown_admin_index import index
    index.exposed = True

    # from shutthatdown_admin_newquote import new_quote
    # new_quote.exposed = True

    # from shutthatdown_admin_newperson import new_person
    # new_person.exposed = True
    
    from shutthatdown_admin_tag_quote import tag_quote
    tag_quote.exposed = True

def main():

    import os.path
    
    parent_dir = os.path.split(os.path.dirname(os.path.abspath(__file__)))[:-1][0]

    cherrypy.root = Root()

    cherrypy.config.update({'server.socket_port': 8080,
                            'server.socket_host': '127.0.0.1',
                            'log.screen': True,
                            'log.error_file': 'site.log',
                            'server.environment': 'production',
                            })

    conf = {'/css': {'tools.staticdir.on': True,
                      'tools.staticdir.dir': os.path.join(parent_dir, 'css'),},
            '/js': {'tools.staticdir.on': True,
                      'tools.staticdir.dir': os.path.join(parent_dir, 'js'),}
        }
    
    cherrypy.quickstart(cherrypy.root, '/', config=conf)

if __name__ == '__main__':
    main()

