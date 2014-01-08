def random_quote(self, **kwargs):

    """ Returns a random quote.
    """

    del kwargs

    database_connection = psycopg2.connect(self.database_connection_details)
    database_cursor = database_connection.cursor()
    database_cursor.execute("select id from quotes where quote_text != ''")

    quotes_tuple = database_cursor.fetchall()
    available_quotes = []

    for quote_id in quotes_tuple:
        available_quotes.append(quote_id[0])

    database_connection.close()

    kwargs = {'quote_id': random.choice(available_quotes)}

    return self.quote(**kwargs)
