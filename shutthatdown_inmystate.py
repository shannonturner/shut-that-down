import psycopg2
import shutthatdown_credentials

def inmystate(self, **kwargs):

    """ Cherrypy.Root.inmystate(): shutthatdown.com/inmystate
    """

    state = kwargs.get('state')
    del kwargs

    state_list = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

    page_source = []

    page_source.append('<div class="row"> <div class="small-8 small-centered columns"> <table cellpadding=4 style="vertical-align: middle; text-align: center;">')
    page_source.append('<tr><td><h2>Shut That Down - Browse By State</h2></td></tr></table></div></div>')

    page_source.append('<div class="row"> <div class="small-4 small-centered columns">')
    page_source.append('<form id="change_page" name="change_page" method="get" action="inmystate"><select name="state" onChange="document.forms[\'change_page\'].submit();"><option value="">Choose your state</option>')

    for iter_state in state_list:
        if state == iter_state:
            page_source.append('<option value="{0}" selected>{0}</option>\n'.format(iter_state))
        else:
            page_source.append('<option value="{0}">{0}</option>\n'.format(iter_state))

    page_source.append('</select></form> </div> </div>')
    
    page_source.append('<div class="row"> <div class="small-8 small-centered columns">')

    with open("statemap.txt") as state_map_file:
            state_map = state_map_file.read()

    for index, iter_state in enumerate(state_list):
        state_map = state_map.replace('<b>{0}</b>'.format(iter_state), '<a href="inmystate?state={0}"><b>{0}</b>'.format(iter_state))

    if state is None or state not in state_list:
        page_source.append(state_map)
    else:

        database_connection = psycopg2.connect(shutthatdown_credentials.database_connection_details)
        database_cursor = database_connection.cursor()
        database_cursor.execute("select persons.id, persons.display_name, persons.type, quotes.id, quotes.quote_text from persons inner join quotes on quotes.who_said = persons.id where quote_text != '' and persons.state = '{0}'".format(state))

        quotes = []

        for one_quote in database_cursor.fetchall():
            (person_id, person_displayname, person_type, quote_id, quote_text) = one_quote
            quotes.append({'person_id': person_id, 'name': person_displayname, 'type': str(person_type).replace("1", "Politician").replace("2", "Media Figure").replace("3", "Other public figure"), 'quote_id': quote_id, 'text': quote_text})

        # Build the tables

        page_source.append('<table cellpadding=4 style="vertical-align: middle; text-align: center;">')
        page_source.append('<tr><td colspan=3><h2>Quotes from <br> Politicians and Media Figures in {0}</h2></td></tr>'.format(state))

        for quote in quotes:
            page_source.append('<tr><td><a href="quote?quote_id={0}"><b>{1}</b></a></td><td>{2}</td><td><a href="quote?quote_id={0}"><b>{3}</b></a></td></tr>'.format(quote['quote_id'], quote['name'], quote['type'], quote['text']))

        if len(quotes) < 1:
            page_source.append('<tr><td><i>There isn\'t anything here just yet, but we\'re adding new quotes all the time!</i></td></tr>')

        database_cursor.close()

        page_source.append(state_map)

    page_source.append('</div></div>')

    return wrap_in_css(page_source, "In My State - Shut That Down")
