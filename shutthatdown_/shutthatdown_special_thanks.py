def special_thanks(self, **kwargs):

    """ shutthatdown.com/special_thanks
    """

    del kwargs

    import psycopg2
    import shutthatdown_.shutthatdown_credentials as shutthatdown_credentials

    from shutthatdown_ import shutthatdown_wrapincss
    wrap_in_css = shutthatdown_wrapincss.wrap_in_css

    database_connection = psycopg2.connect(shutthatdown_credentials.database_connection_details)
    database_cursor = database_connection.cursor()

    thanks_query = "select distinct on (persons.display_name) persons.display_name, quotes.id from persons inner join quotes on quotes.who_said = persons.id where quote_text != ''"
    database_cursor.execute(thanks_query)

    thanks_list = []

    for one_person in database_cursor.fetchall():
        (who_said, quote_id) = one_person
        thanks_list.append('<a href="quote?quote_id={0}"> {1} </a> <b>|</b> '.format(quote_id, who_said))

    thanks_list[-1] = thanks_list[-1][:-9] # removes the trailing separator from the last person
        
    page_source = []

    page_source.append('<div class="row"> <div class="small-12 small-centered columns"> <table cellpadding=4 style="vertical-align: middle; text-align: center;">')
    page_source.append('<tr><td colspan=3><h2>Shut That Down would like to give a special thanks to everyone listed below for reminding us every day of the importance of our work:</h2></td></tr>')
    page_source.append('<tr><td>')

    page_source.extend(thanks_list)
    page_source.append('</td></tr><tr><td><b> ... and many, many more. </b> </td></tr></table> </div></div>')

    database_connection.close()

    return wrap_in_css(page_source, 'Special Thanks - Shut That Down')
