def search(self, **kwargs):

    """ Basic search functionality; searches on quote text and person's name.
    """

    query = kwargs.get('query')
    del kwargs

    if query is not None:

        query = str(query)

        sanitized_query = []
        for char in query:
            if char.isalpha() is True or char.isspace() is True or char.isdigit() is True:
                sanitized_query.append(char)

        query = ''.join(sanitized_query)

        query.replace("'", "").replace('"', '').replace("\\","").replace("`","")

        search_query = "select persons.id, persons.display_name, persons.type, quotes.id, quotes.quote_text from persons inner join quotes on quotes.who_said = persons.id where quote_text != '' and ("

        query = query.split(" ")
        for word in query:
            search_query += " persons.display_name ilike '%{0}%' or quotes.quote_text ilike '%{0}%' or".format(word)

        query = " ".join(query)

        search_query = "{0})".format(search_query[:-2]) # removes the trailing "or" and closes the parenthesis

        database_connection = psycopg2.connect(self.database_connection_details)
        database_cursor = database_connection.cursor()

        database_cursor.execute(search_query)

        quotes = []

        for one_quote in database_cursor.fetchall():
            (person_id, person_displayname, person_type, quote_id, quote_text) = one_quote
            quotes.append({'person_id': person_id, 'name': person_displayname, 'type': str(person_type).replace("1", "Politician").replace("2", "Media Figure").replace("3", "Other public figure"), 'quote_id': quote_id, 'text': quote_text})

        # Build the tables

        page_source = []
        
        page_source.append('<div class="row"> <div class="small-12 small-centered columns"> <table cellpadding=4 style="vertical-align: middle; text-align: center;">')
        page_source.append('<tr><td colspan=3><h2>Searching quote text and names of people for: {0}</h2></td></tr>'.format(str(query)))

        for quote in quotes:
            page_source.append('<tr><td><a href="quote?quote_id={0}"><b>{1}</b></a></td><td>{2}</td><td><a href="quote?quote_id={0}"><b>{3}</b></a></td></tr>'.format(quote['quote_id'], quote['name'], quote['type'], quote['text']))

        page_source.append('</table> </div> </div>')

        database_connection.close()

        return wrap_in_css(page_source, 'Search Shut That Down: {0}'.format(str(query)))

    else:
        return self.index()
