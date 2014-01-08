def welove(self, **kwargs):

    """ Cherrypy.Root.welove(): shutthatdown.com/welove
    """

    del kwargs

    page_source = []

    page_source.append('<div class="row"> <div class="small-12 small-centered columns"> <table cellpadding=4 style="vertical-align: middle; text-align: center;">')
    page_source.append('<tr><td><h2>Who we love</h2></td></tr>')
    page_source.append('<tr><td><b>Shut That Down</b> would like to send an internet hug across the series of tubes to the following lovely people:</td></tr><tr><td>')

    with open("welove.txt") as welove_filename:
        welove = welove_filename.read()
        welove = welove.split('\n')

        page_source.extend('</td></tr><tr><td>'.join(welove))

    page_source.append('If you love Shut That Down, consider a donation to those good folks doing great work on tiny budgets.</td></tr></table> </div></div>')

    return wrap_in_css(page_source, "Shut That Down Loves ...")
