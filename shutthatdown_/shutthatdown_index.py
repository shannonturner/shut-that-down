def index(self, **kwargs):

    """ shutthatdown.com/ 
    """

    error_message = kwargs.get('error_message')
    
    del kwargs # Having kwargs defined in the function definition means if someone uses /index?some_unhandled_parameter=something, their page won't crash

    import psycopg2
    import shutthatdown_.shutthatdown_credentials as shutthatdown_credentials

    from shutthatdown_ import shutthatdown_wrapincss
    wrap_in_css = shutthatdown_wrapincss.wrap_in_css

    database_connection = psycopg2.connect(shutthatdown_credentials.database_connection_details)
    database_cursor = database_connection.cursor()

    database_cursor.execute("select persons.id, persons.display_name, persons.sunlight_id, quotes.id, quotes.quote_text from persons inner join quotes on persons.id = quotes.who_said where persons.sunlight_id != '' and quotes.quote_text != '' and persons.type = 1 order by random() limit 1")

    (person_id, person_displayname, sunlight_id, quote_id, quote_text) = database_cursor.fetchone()

    recent_activity_query = "select date, event, count(event) from recent_activity group by date, event order by date desc, event asc limit 5"
    database_cursor.execute(recent_activity_query)

    activity_source = []

    activity_source.append('<table cellpadding=2 style="vertical-align: middle; text-align: center;"><tr><td>Recent Activity</td></tr>')

    for activity in database_cursor.fetchall():
            (event_date, event, event_count) = activity
            activity_source.append('<tr><td>{0} new {1} added on {2}</td></tr>'.format(event_count, str(event).replace('1', 'quotes').replace('2', 'people').replace('3', 'organizations'), event_date))
    
    activity_source.append('</table>')

    # Build the page

    page_source = []

    if error_message is None:
        page_source.append('<!--Page Loaded Successfully-->') # Replace this when error handling
    else:
        page_source.append('<div class="row"> <div class="small-8 small-centered columns"> <p> <br> <i>{0}</i> <br> </p> </div> </div>'.format(error_message))

    page_source.append('<div class="row"> <div class="small-8 small-centered columns"> <table cellpadding=4 style="vertical-align: middle; text-align: center;">')

    with open('static/index.html') as static_index:
        page_source.append(static_index.read())

    quote_source = []

    quote_source.append('<div class="row"> <div class="small-8 small-centered columns"> <table cellpadding=8 style="vertical-align:middle; text-align:center;"><tr><td><h2><b><a href="quote?quote_id={0}">{1}</a></b></h2></td></tr>'.format(quote_id, person_displayname))

    quote_source.append('<tr><td><h3>"{0}"</h3></td></tr></table> </div> </div>'.format(quote_text))

    try:
        sunlight_pol_url = 'http://transparencydata.com/api/1.0/aggregates/pol/{0}/contributors.json?&apikey={1}'.format(sunlight_id, sunlight_apikey)
        sunlight_contributions_list = json.loads(urllib2.urlopen(sunlight_pol_url).read())
    except urllib2.HTTPError:
        sunlight_contributions_list = []
    
    page_source.extend(quote_source)

    donors_source = []
            
    if len(sunlight_contributions_list) > 0:

        donors_source.append('<div class="row"> <div class="small-8 small-centered columns">')

        donors_source.append('<table cellpadding=4 style="vertical-align: middle; text-align: center;"><tr><td colspan=5><b>All-time largest donors to <b>{0}</b> (how interesting!)</td></tr>'.format(person_displayname))
        donors_source.append('<tr><td><b>More Info</b></td><td><b>Donor</b></td><td><b>Total Given</b></td><td><b>Directly Given</b></td><td><b>Given by Employees</b></td></tr>')

        for contribution in sunlight_contributions_list: # Sunlight's Influence Explorer breaks donations down by direct vs. employees, which is preferred.

            if contribution['id'] is not None:
                donors_source.append('<tr><td><a href="http://influenceexplorer.com/organization/{0}/{1}" target="_blank"><img height=33 width=33 src="icons/sunlight.png" title="View {2} on Sunlight\'s Influence Explorer" alt="View {2} on Sunlight\'s Influence Explorer"></a>\n'.format(contribution['name'].lower().replace('/','').replace(' ','-').replace(' & ',' ').replace('&',''), contribution['id'], contribution['name']))
            else:
                donors_source.append('<tr><td>')

            donors_source.append('</td><td>{0}</td><td>${1:,}</td><td>${2:,}</td><td>${3:,}</td></tr>'.format(contribution['name'], int(float(contribution['total_amount'])), int(float(contribution['direct_amount'])), int(float(contribution['employee_amount']))))
            
        donors_source.append('<tr><td colspan=5>Donation information provided by the <a href="http://sunlightfoundation.com/" target="_blank">Sunlight Foundation</a>, <a href="http://opensecrets.org/" target="_blank">OpenSecrets.org</a>, and <a href="http://followthemoney.org" target="_blank">FollowTheMoney.org</a></td></tr></table>\n</div> </div>')
           
        page_source.extend(donors_source)

    page_source.append('<div class="row"> <div class="small-4 small-centered columns">')
    page_source.extend(activity_source)
    page_source.append('</div> </div>')

    database_connection.close()

    return wrap_in_css(page_source, 'Shut That Down')
