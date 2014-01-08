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
