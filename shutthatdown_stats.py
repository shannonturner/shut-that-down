def stats(self, **kwargs):

    """ Cherrypy.Root.stats: shutthatdown.com/stats
    """

    del kwargs

    page_source = []

    database_connection = psycopg2.connect(self.database_connection_details)
    database_cursor = database_connection.cursor()

    # Number of Quotes in the Database
    database_cursor.execute("select count(*) from quotes where quote_text != ''")
    quote_count = database_cursor.fetchone()[0]

    # Number of Organizations in the Database
    database_cursor.execute("select count(*) from organizations")
    org_count = database_cursor.fetchone()[0]

    # Number of Advertisers in the Database
    # TODO

    # Number of Quotes by Gender
    quotes_by_gender = []
    database_cursor.execute("select gender, count(*) from quotes inner join persons on persons.id = quotes.who_said where quote_text != '' and gender != '' group by gender order by count(*) desc")
    for quotecount_by_gender in database_cursor.fetchall():
        (gender, count) = quotecount_by_gender
        quotes_by_gender.append('<tr><td><h3><b>{0} ({1:0.4}%)</b></h3> of quotes are by {2}</td></tr>'.format(count, (float(count) / float(quote_count))*100, gender.replace("M", "men").replace("F", "women")))

    # Number of Quotes by Party
    quotes_by_party = []
    database_cursor.execute("select party, count(*), (select count(*) from quotes inner join persons on persons.id = quotes.who_said where quote_text != '' and party != '' and persons.type in (1,3) order by count(*) desc) from quotes inner join persons on persons.id = quotes.who_said where quote_text != '' and party != '' and persons.type in (1,3) group by party order by count(*) desc")
    for quotecount_by_party in database_cursor.fetchall():
        (party, count, total) = quotecount_by_party
        quotes_by_party.append('<tr><td><h3><b>{0} ({1:0.4}%)</b></h3> of quotes are by {2} party members</td></tr>'.format(count, (float(count) / float(total))*100, party.replace("R", "Republican").replace("D", "Democratic").replace("I", "Independent")))
        
    # Number of Quotes by Quote Type
    quotes_by_type = []
    database_cursor.execute("select (select count(*) from quote_issues where issue_id = 1) as Misogynist, (select count(*) from quote_issues where issue_id = 2) as Racist, (select count(*) from quote_issues where issue_id = 3) as Xenophobic, (select count(*) from quote_issues where issue_id = 4) as AntiLGBT")
    for quotecount_by_type in database_cursor.fetchall():
        quotes_by_type.append('<tr><td><h4><b>{0} ({1:0.4}%)</b></h4> of quotes are misogynist in nature</td></tr>'.format(quotecount_by_type[0], (float(quotecount_by_type[0]) / sum(quotecount_by_type[:]))*100))
        quotes_by_type.append('<tr><td><h4><b>{0} ({1:0.4}%)</b></h4> of quotes are racist in nature</td></tr>'.format(quotecount_by_type[1], (float(quotecount_by_type[1]) / sum(quotecount_by_type[:]))*100))
        quotes_by_type.append('<tr><td><h4><b>{0} ({1:0.4}%)</b></h4> of quotes are xenophobic in nature</td></tr>'.format(quotecount_by_type[2], (float(quotecount_by_type[2]) / sum(quotecount_by_type[:]))*100))
        quotes_by_type.append('<tr><td><h4><b>{0} ({1:0.4}%)</b></h4> of quotes are homophobic or transphobic in nature</td></tr>'.format(quotecount_by_type[3], (float(quotecount_by_type[3]) / sum(quotecount_by_type[:]))*100))
         
    page_source.append('<div class="row"> <div class="small-5 small-centered columns"> <table cellpadding=4 style="vertical-align: middle; text-align: center;">')
    page_source.append('<tr><td><h2>Shut That Down has ...</h2></td></tr>')

    page_source.append('<tr><td><h3><b>{0}</b></h3> quotes</td></tr>'.format(quote_count))
    page_source.append('<tr><td><h3><b>{0}</b></h3> organizations - and who they\'ve donated to</td></tr>'.format(org_count))

    page_source.append('<tr><td>&nbsp;</td></tr>')
    page_source.extend(quotes_by_gender)
    page_source.append('<tr><td>&nbsp;</td></tr>')
    page_source.extend(quotes_by_party)
    page_source.append('<tr><td>&nbsp;</td></tr>')
    page_source.extend(quotes_by_type)
    page_source.append('<tr><td>&nbsp;</td></tr>')

    page_source.append('<tr><td> ... kinda makes you think, doesn\'t it? </td></tr></table></div></div>')

    database_connection.close()

    return wrap_in_css(page_source, 'Stats - Shut That Down')
