def enablers(self, **kwargs):

    """ shutthatdown.com/enablers
    """

    del kwargs

    import psycopg2
    import shutthatdown_.shutthatdown_credentials as shutthatdown_credentials

    from shutthatdown_ import shutthatdown_wrapincss
    wrap_in_css = shutthatdown_wrapincss.wrap_in_css

    page_source = []

    database_connection = psycopg2.connect(shutthatdown_credentials.database_connection_details)
    database_cursor = database_connection.cursor()

    database_cursor.execute('select organizations.name, organizations.sunlight_id from organizations order by organizations.name')

    org_table = []
    
    for (org_name, sunlight_id) in database_cursor.fetchall():
        if sunlight_id is None:
            if org_name != 'BLANK' and org_name.count(",") != 1 and org_name.isupper() == False:
                org_table.append('<tr><td><b>{0}</b></td></tr>'.format(org_name))
        else:  
            org_table.append('<tr><td><b><a href="http://influenceexplorer.com/organization/{0}/{1}" target="_blank">{2}</a></b></td></tr>'.format(org_name.lower().replace(" ","-").replace(' & ',' ').replace('&',''), sunlight_id, org_name))                

    database_cursor.execute("select persons.display_name, quotes.id from persons inner join quotes on persons.id = quotes.who_said where type = 1 and quote_text != '' order by random() limit 1")
    (one_politician, politician_quote) = database_cursor.fetchone()[:]

    database_cursor.execute("select persons.display_name, quotes.id from persons inner join quotes on persons.id = quotes.who_said where type = 2 and quote_text != '' order by random() limit 1")
    (one_mediafigure, mediafigure_quote) = database_cursor.fetchone()[:]

    page_source.append('<div class="row"> <div class="small-12 small-centered columns"> <table cellpadding=4 style="vertical-align: middle; text-align: center;">')

    page_source.append('<tr><td><h2>These organizations are the enablers who keep people like <a href="quote?quote_id={0}" target="_blank">{1}</a> in power and <a href="quote?quote_id={2}" target="_blank">{3}</a> on the air.</h2></td></tr>'.format(politician_quote, one_politician, mediafigure_quote, one_mediafigure))

    page_source.extend(org_table)

    page_source.append('</table> </div> </div>')

    database_connection.close()

    return wrap_in_css(page_source, "Enablers - Shut That Down")
