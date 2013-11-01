import cherrypy

class Root(object):


    from shutthatdown_admin_index import index as index
    index.exposed = True

    from shutthatdown_admin_newquote import newquote as newquote
    newquote.exposed = True
    
    from shutthatdown_admin_tag_quote import tag_quote as tag_quote
    tag_quote.exposed = True


def wrap_in_css(source, title):

    """ wrap_in_css(source, title): Adds the CSS header and footer to the page source and returns the result in a easier to read format with plenty of whitespace.
    """

    source = ''.join(source)

    with open("cssheader.txt") as header_filename:
        header = header_filename.read()
        header = header.replace('<title>!!!DYNAMIC_TITLE!!!', '<title>{0}'.format(title))
        source = '{0}{1}'.format(header, source)

    with open("cssfooter.txt") as footer_filename:
        footer = footer_filename.read()
        source = '{0}{1}'.format(source, footer)

    return source.replace("<table", "\n<table").replace("<tr", "\n\t<tr").replace("<td", "\n\t\t<td").replace("</td>", "\n\t\t</td>").replace("</tr>", "\n\t</tr>").replace("</table>","\n</table>\n").replace('<div','\n\n<div').replace('</div>', '\n\n</div>\n\n')

def main():

    cherrypy.quickstart(Root(), '/', 'admincfg.cfg')

if __name__ == '__main__':
    main()
