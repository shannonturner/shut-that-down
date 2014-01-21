def browse_quotes(self, **kwargs):

    """ shutthatdown.com/browse_quotes
    """

    quote_type = kwargs.get('quote_type')
    page_start = kwargs.get('start')
    page_end = kwargs.get('end')
    del kwargs

    import psycopg2
    import shutthatdown_.shutthatdown_credentials as shutthatdown_credentials

    from shutthatdown_ import shutthatdown_wrapincss
    wrap_in_css = shutthatdown_wrapincss.wrap_in_css

    database_connection = psycopg2.connect(shutthatdown_credentials.database_connection_details)
    database_cursor = database_connection.cursor()

    browse_query = "WITH PAGINATION AS ( SELECT DISTINCT ON (quotes.id) ROW_NUMBER() OVER (ORDER BY  quotes.id ) RETURN_ITEMS, persons.id, persons.display_name, persons.type, quotes.id, quotes.quote_text from persons inner join quotes on quotes.who_said = persons.id inner join quote_issues on quotes.id = quote_issues.quote_id where quote_text != ''-- AND ANY ADDITIONAL CONDITIONS ) SELECT * FROM PAGINATION WHERE RETURN_ITEMS Between --START and --END"
    total_quotes_query = "select count(distinct quotes.id) from quotes inner join persons on quotes.who_said = persons.id inner join quote_issues on quotes.id = quote_issues.quote_id where quote_text != '' -- AND ANY ADDITIONAL CONDITIONS"

    try:
        if int(quote_type) in (1,2,3,4):            
            browse_query = browse_query.replace("-- AND ANY ADDITIONAL CONDITIONS"," and quote_issues.issue_id = {0}".format(quote_type))
            total_quotes_query = total_quotes_query.replace("-- AND ANY ADDITIONAL CONDITIONS"," and quote_issues.issue_id = {0}".format(quote_type))

        if int(quote_type) == 1:
            table_heading = '<h2>Misogynist quotes</h2>'
        elif int(quote_type) == 2:
            table_heading = '<h2>Racist quotes</h2>'
        elif int(quote_type) == 3:
            table_heading = '<h2>Xenophobic quotes</h2>'
        elif int(quote_type) == 4:
            table_heading = '<h2>Homophobic and Transphobic quotes</h2>'
        else:
            quote_type = None
            
    except TypeError:
        quote_type = None
    except ValueError:
        quote_type = None

    if quote_type is None: # At this point if "-- AND ANY ADDITIONAL CONDITIONS" is still in the query, it's because there weren't any additional conditions to replace.
        table_heading = '<h2>All quotes</h2>'
        quote_type = 0
        browse_query = browse_query.replace("-- AND ANY ADDITIONAL CONDITIONS", "")
        total_quotes_query = total_quotes_query.replace("-- AND ANY ADDITIONAL CONDITIONS","")

    try:
        page_start = abs(int(page_start))
    except TypeError:
        page_start = 1
    except ValueError:
        page_start = 1

    try:
        page_end = abs(int(page_end))
    except TypeError:
        page_end = page_start + 24
    except ValueError:
        page_end = page_start + 24

    browse_query = browse_query.replace("--START", str(page_start))
    browse_query = browse_query.replace("--END", str(page_end))

    database_cursor.execute(total_quotes_query)
    total_quotes = database_cursor.fetchone()[0]

    database_cursor.execute(browse_query)

    quotes = []

    for one_quote in database_cursor.fetchall():
        (returnitems_id, person_id, person_displayname, person_type, quote_id, quote_text) = one_quote
        quotes.append({'person_id': person_id, 'name': person_displayname, 'type': str(person_type).replace("1", "Politician").replace("2", "Media Figure").replace("3", "Other public figure"), 'quote_id': quote_id, 'text': quote_text})

    # Build the tables

    page_source = []

    page_source.append('<div class="row"> <div class="small-12 small-centered columns"> <table cellpadding=4 style="vertical-align: middle; text-align: center;">')
    page_source.append('<tr><td colspan=3>{0}</td></tr>'.format(table_heading))

    if len(quotes) > 0:
        for quote in quotes:
            page_source.append('<tr><td><a href="quote?quote_id={0}"><b>{1}</b></a></td><td>{2}</td><td><a href="quote?quote_id={0}"><b>{3}</b></a></td></tr>'.format(quote['quote_id'], quote['name'], quote['type'], quote['text']))

    page_source.append('</table> </div> </div>')

    page_source.append('<div class="row"> <div class="small-3 small-centered columns"> <table cellpadding=4 style="vertical-align: middle; text-align: right;">')
    page_source.append('<tr><td>Displaying {0} to {1} out of {2}</td></tr> <tr><td>'.format(page_start, min([page_end, total_quotes]), total_quotes))

    if page_start != 1: # If it's not at the beginning, add a link to the beginning
        page_source.append('<a href="browse_quotes?quote_type={0}&start=1"><u>&lt;&lt; First </u></a>'.format(quote_type))
    if page_start >= 26: # If it's greater than 25, add a link to the previous page in addition to the beginning
        page_source.append(' | <a href="browse_quotes?quote_type={0}&start={1}"><u> &lt; Previous </u></a>'.format(quote_type, page_start - 25))

    if page_start + 24 < total_quotes: # If it's not at the end, add a link to go to the next and end
        page_source.append(' | <a href="browse_quotes?quote_type={0}&start={1}"><u> &gt; Next </u></a>'.format(quote_type, page_end+1))
        page_source.append(' | <a href="browse_quotes?quote_type={0}&start={1}"><u> &gt;&gt; Last </u></a>'.format(quote_type, total_quotes - 24))

    page_source.append('</td></tr></table></div></div>')

    database_connection.close()

    return wrap_in_css(page_source, 'Browse')
