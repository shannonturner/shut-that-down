import psycopg2
import shutthatdown_credentials
from crpapi import CRP, CRPApiError

def quote(self, **kwargs):

    """ Cherrypy.Root.quote(): shutthatdown.com/quote
    """

    quote_id = kwargs.get('quote_id')
    cycle = kwargs.get('cycle')

    del kwargs

    """ Cherrypy.Root.quote(): The page where a quote, who said it, and who donated to them, is displayed. """

    page_source = []

    # Get quote and attribution from database

    try:
        quote_id = int(quote_id)
        if quote_id < 1:
            return self.index()
    except ValueError:
        return self.index()
    except TypeError:
        return self.index()

    try:
        cycle = int(cycle)
        if cycle < 1980 or cycle > 2040: # What's the best way to guarantee 'this epoch'?
            cycle = None
    except ValueError:
        cycle = None
    except TypeError:
        cycle = None

    select_quote_query = "select persons.id, persons.crp_id, persons.bioguide_id, persons.littlesis_id, persons.littlesis_name, persons.sunlight_id, persons.display_name, persons.first_name, persons.last_name, persons.type, persons.gender, persons.party, persons.state, quotes.who_said, quotes.quote_text from persons join quotes on quotes.who_said = persons.id where quotes.id = {0}".format(quote_id)

    database_connection = psycopg2.connect(self.database_connection_details)
    database_cursor = database_connection.cursor()
    database_cursor.execute(select_quote_query)

    try:
        (person_id, crp_id, bioguide_id, littlesis_id, littlesis_name, sunlight_id, person_displayname, person_firstname, person_lastname, person_type, person_gender, person_party, person_state, who_said, quote_text) = database_cursor.fetchone()
    except TypeError, e:
        if "'NoneType' object is not iterable" in e:
            return self.index()

    # Get other quotes by this person if they exist

    select_other_quotes_query = "select quotes.id, quotes.quote_text from quotes where quotes.who_said = {0} and quotes.id != {1}".format(who_said, quote_id)
    database_cursor.execute(select_other_quotes_query)

    other_quotes = []

    for one_quote in database_cursor.fetchall():
        (other_quote_id, other_quote_text) = one_quote
        other_quotes.append('<tr><td><a href="quote?quote_id={0}">{1}</a></td></tr>'.format(other_quote_id, other_quote_text))

    # Get external data from APIs (Sunlight's Congress and Influence Explorer, Center for Responsive Politics' Open Secrets, Little Sis)

    if person_type == 1: # Politician

        if bioguide_id is None and crp_id is None:
            
            # Search Sunlight's Congress API for this politician

            try:
                sunlight_search_url = 'http://congress.api.sunlightfoundation.com/legislators?apikey={0}&query={1}&all_legislators=true'.format(sunlight_apikey, person_lastname)
                sunlight_search_summary = json.loads(urllib2.urlopen(sunlight_search_url).read())
            except urllib2.HTTPError:
                sunlight_search_summary = {}

            try:

                for sunlight_search_item in sunlight_search_summary['results']:

                    if (sunlight_search_item['first_name'] == person_firstname and sunlight_search_item['last_name'] == person_lastname and (sunlight_search_item['state'] == person_state or person_state is None)):

                        if sunlight_search_item['crp_id'] is not None:
                            database_cursor.execute("update persons set crp_id = '{0}' where id = {1}".format(sunlight_search_item['crp_id'], person_id))
                            database_connection.commit()
                            crp_id = sunlight_search_item['crp_id']

                        if sunlight_search_item['bioguide_id'] is not None:
                            database_cursor.execute("update persons set bioguide_id = '{0}' where id = {1}".format(sunlight_search_item['bioguide_id'], person_id))
                            database_connection.commit()
                            bioguide_id = sunlight_search_item['bioguide_id']

                        sunlight_congress_summary = sunlight_search_item

                        sunlight_politician_summary = {}

                        break
                else:
                    sunlight_congress_summary = {}

            except KeyError:    
                sunlight_congress_summary = {}

        else:

            # Using either the bioguide_id or crp_id, check Sunlight's Congress API for this politician

            if bioguide_id is not None:
                sl_parameters = {'bioguide_id': bioguide_id}
            elif crp_id is not None:
                sl_parameters = {'crp_id': crp_id}

            try:
                sunlight_congress_url = 'http://congress.api.sunlightfoundation.com/legislators?apikey={0}&{1}&all_legislators=true'.format(sunlight_apikey, urllib.urlencode(sl_parameters))
                sunlight_congress_summary = json.loads(urllib2.urlopen(sunlight_congress_url).read())['results']
            except urllib2.HTTPError:
                sunlight_congress_summary = {}

            sunlight_politician_summary = {}

            if len(sunlight_congress_summary) > 0:

                if len(sunlight_congress_summary) == 1:
                    sunlight_congress_summary = sunlight_congress_summary.pop()

                if bioguide_id is None and sunlight_congress_summary['bioguide_id'] is not None:
                    database_cursor.execute("update persons set bioguide_id = '{0}' where id = {1}".format(sunlight_congress_summary['bioguide_id'], person_id))
                    database_connection.commit()
                    bioguide_id = sunlight_congress_summary['bioguide_id']

                if crp_id is None and sunlight_congress_summary['crp_id'] is not None:
                    database_cursor.execute("update persons set bioguide_id = '{0}' where id = {1}".format(sunlight_congress_summary['crp_id'], person_id))
                    database_connection.commit()
                    crp_id = sunlight_congress_summary['crp_id']

                if person_gender is None and sunlight_congress_summary['gender'] is not None:
                    database_cursor.execute("update persons set gender = '{0}' where id = {1}".format(sunlight_congress_summary['gender'], person_id))
                    database_connection.commit()
                    person_gender = sunlight_congress_summary['gender']

                if person_party is None and sunlight_congress_summary['party'] is not None:
                    database_cursor.execute("update persons set party = '{0}' where id = {1}".format(sunlight_congress_summary['party'], person_id))
                    database_connection.commit()
                    person_party = sunlight_congress_summary['party']

                if person_state is None and sunlight_congress_summary['state'] is not None:
                    database_cursor.execute("update persons set state = '{0}' where id = {1}".format(sunlight_congress_summary['state'], person_id))
                    database_connection.commit()
                    person_state = sunlight_congress_summary['state']

        if (sunlight_id is None and (bioguide_id is not None or crp_id is not None)): 

            # Use Sunlight's ID Lookup for Influence Explorer

            if bioguide_id is not None:
                sunlight_ie_url = 'http://transparencydata.com/api/1.0/entities/id_lookup.json?apikey={0}&bioguide_id={1}'.format(sunlight_apikey, bioguide_id)

            else: # Prefer bioguide_id; use crp_id as backup

                if crp_id is not None:
                    sunlight_ie_url = 'http://transparencydata.com/api/1.0/entities/id_lookup.json?apikey={0}&namespace=urn:crp:recipient&id={1}'.format(sunlight_apikey, crp_id)

            try:
                sunlight_ie_id = json.loads(urllib2.urlopen(sunlight_ie_url).read())[0]['id']
            except urllib2.HTTPError:
                sunlight_ie_id = None
            
            if sunlight_ie_id is not None and sunlight_id is None:
                database_cursor.execute("update persons set sunlight_id = '{0}' where id = {1}".format(sunlight_ie_id, person_id))
                database_connection.commit()
                sunlight_id = sunlight_ie_id

        if sunlight_id is not None:

            try:
                sunlight_ie_url = 'http://transparencydata.com/api/1.0/entities/{0}.json?apikey={1}'.format(sunlight_id, sunlight_apikey)
                sunlight_ie_summary = json.loads(urllib2.urlopen(sunlight_ie_url).read())
            except urllib2.HTTPError:
                sunlight_ie_summary = {}

            try:
                sunlight_external_url_polname = sunlight_ie_summary['name'][:sunlight_ie_summary['name'].index('(')].strip().lower().replace(" ","-")
                sunlight_external_url_politician = "http://influenceexplorer.com/politician/{0}/{1}".format(sunlight_external_url_polname, sunlight_id)
            except ValueError:
                sunlight_external_url_polname = None
                sunlight_external_url_politician = None
            except KeyError:
                sunlight_external_url_polname = None
                sunlight_external_url_politician = None

        if crp_id is not None:
            if cycle is None:
                try:
                    politician_summary = CRP.candSummary.get(cid=crp_id)
                    cycle = politician_summary['cycle']
                except CRPApiError:
                    cycle = None
                
            else:
                try:
                    politician_summary = CRP.candSummary.get(cid=crp_id, cycle=cycle)
                except CRPApiError:
                    politician_summary = {}

        else:

            # If sunlight_id, bioguide_id, and crp_id are all None, look Sunlight's up, then get the sunlight_congress_summary (if applicable) and the sunlight_ie_summary from Influence Explorer

            if sunlight_id is None and bioguide_id is None and crp_id is None:

                try:
                    sunlight_lookup_url = 'http://transparencydata.org/api/1.0/entities.json?apikey={0}&search={1}+{2}&type=politician'.format(sunlight_apikey, person_firstname, person_lastname)
                    sunlight_id_response = json.loads(urllib2.urlopen(sunlight_lookup_url).read())
                except urllib2.HTTPError:
                    sunlight_id_response = []
                
                if len(sunlight_id_response) == 1:
                    sunlight_id_response = sunlight_id_response.pop()
                elif len(sunlight_id_response) > 1:

                    for sunlight_id_check in sunlight_id_response:
                        if (((person_state is None or sunlight_id_check['state'] == person_state) and (person_party is None or sunlight_id_check['party'] == person_party) and (sunlight_id_check['name'].lower() == "{0}, {1}".format(person_lastname, person_firstname).lower() or sunlight_id_check['name'].lower() == "{0} ({1})".format(person_displayname, person_party).lower()))):
                            sunlight_id_response = sunlight_id_check
                            break
                    else:
                        # This is more permissive but it comes at the risk of an incorrect match
                        for sunlight_id_check in sunlight_id_response:
                            if (person_lastname.lower() in sunlight_id_check['name'].lower() and person_firstname.lower() in sunlight_id_check['name'].lower() and (person_party is None or person_party == sunlight_id_check['party'] and (person_state is None or person_state == sunlight_id_check['state']))):
                                sunlight_id_response = sunlight_id_check
                                break
                        else:
                            sunlight_id_response = [] # No perfect match

                if len(sunlight_id_response) > 0:
                    if sunlight_id_response['id'] is not None:
                        database_cursor.execute("update persons set sunlight_id = '{0}' where id = {1}".format(sunlight_id_response['id'], person_id))
                        database_connection.commit()
                        sunlight_id = sunlight_id_response['id']

                    if sunlight_id is not None:

                        # Get Data from Influence Explorer
                        try:
                            sunlight_ie_url = 'http://transparencydata.com/api/1.0/entities/{0}.json?apikey={1}'.format(sunlight_id, sunlight_apikey)
                            sunlight_ie_summary = json.loads(urllib2.urlopen(sunlight_ie_url).read())
                        except urllib2.HTTPError:
                            sunlight_ie_summary = {}
                        
                        try:
                            sunlight_external_url_polname = sunlight_ie_summary['name'][:sunlight_ie_summary['name'].index('(')].strip().lower().replace(" ","-")
                            sunlight_external_url_politician = "http://influenceexplorer.com/politician/{0}/{1}".format(sunlight_external_url_polname, sunlight_id)
                        except ValueError:
                            sunlight_external_url_polname = None
                            sunlight_external_url_politician = None
                        except KeyError:
                            sunlight_external_url_polname = None
                            sunlight_external_url_politician = None

                # Search Sunlight's Congress API for this politician
                try:
                    sunlight_search_url = 'http://congress.api.sunlightfoundation.com/legislators?apikey={0}&query={1}&all_legislators=true'.format(sunlight_apikey, person_lastname)
                    sunlight_search_summary = json.loads(urllib2.urlopen(sunlight_search_url).read())
                except urllib2.HTTPError:
                    sunlight_search_summary = {}
                
                try:

                    for sunlight_search_item in sunlight_search_summary['results']:

                        if (sunlight_search_item['first_name'] == person_firstname and sunlight_search_item['last_name'] == person_lastname and sunlight_search_item['state'] == person_state):

                            if sunlight_search_item['crp_id'] is not None:
                                database_cursor.execute("update persons set crp_id = '{0}' where id = {1}".format(sunlight_search_item['crp_id'], person_id))
                                database_connection.commit()
                                crp_id = sunlight_search_item['crp_id']

                            if sunlight_search_item['bioguide_id'] is not None:
                                database_cursor.execute("update persons set bioguide_id = '{0}' where id = {1}".format(sunlight_search_item['bioguide_id'], person_id))
                                database_connection.commit()
                                bioguide_id = sunlight_search_item['bioguide_id']

                            sunlight_congress_summary = sunlight_search_item 

                            sunlight_politician_summary = {}

                            break
                    else:
                        sunlight_congress_summary = {}

                except KeyError:
                    sunlight_congress_summary = {}
            else:
                sunlight_congress_summary = {}
            
        if len(sunlight_congress_summary) == 0: # If the politician is not a US (federal) congressperson, use a different source for their information

            check_cycles = []

            try:
                for check_cycle in sunlight_ie_summary['metadata'].keys():
                    try:
                        check_cycles.append(int(check_cycle))
                    except ValueError, e: # When trying to convert a non-numerical string, e is 'invalid literal for int() with base 10: ...'
                        continue
            except KeyError:
                pass
            except UnboundLocalError:
                # This only occurs if a match wasn't found at all.
                cycle = 2012 # this is a total fudge, I admit.
                sunlight_ie_summary = {}
                sunlight_politician_summary = {}
            else:
                cycle = max(check_cycles)

                sunlight_politician_summary = {}

                sunlight_politician_summary['party'] = sunlight_ie_summary['metadata'][str(cycle)]['party']

                if person_party is None and sunlight_politician_summary['party'] is not None:
                    database_cursor.execute("update persons set party = '{0}' where id = {1}".format(sunlight_politician_summary['party'], person_id))
                    database_connection.commit()
                    person_party = sunlight_politician_summary['party']                

                sunlight_politician_summary['state'] = sunlight_ie_summary['metadata'][str(cycle)]['state']

                if person_state is None and sunlight_politician_summary['state'] is not None:
                    database_cursor.execute("update persons set state = '{0}' where id = {1}".format(sunlight_politician_summary['state'], person_id))
                    database_connection.commit()
                    person_state = sunlight_politician_summary['state']
                
                if sunlight_ie_summary['metadata'][str(cycle)]['seat_result'] == 'W':
                    sunlight_politician_summary['in_office'] = True
                else:
                    sunlight_politician_summary['in_office'] = False 
                if sunlight_ie_summary['metadata'][str(cycle)]['seat_held'] == '': # seat_held is the seat they had previously if any; seat is the office they sought
                    sunlight_politician_summary['office'] = sunlight_ie_summary['metadata'][str(cycle)]['seat']
                else:
                    sunlight_politician_summary['office'] = sunlight_ie_summary['metadata'][str(cycle)]['seat_held']
                
                sunlight_politician_summary['office'] = sunlight_politician_summary['office'].replace('federal:house', 'US House of Representatives').replace('federal:senate', 'US Senate').replace('state:lower', 'State Representative (Lower House)')
                if sunlight_ie_summary['metadata'][str(cycle)]['district_held'] == '': # district_held is the district they had previously if any; district is the district they sought
                    if sunlight_ie_summary['metadata'][str(cycle)]['district'] != '':
                        sunlight_politician_summary['district'] = sunlight_ie_summary['metadata'][str(cycle)]['district']
                    else:
                        sunlight_politician_summary['district'] = None
                else:
                    sunlight_politician_summary['district'] = sunlight_ie_summary['metadata'][str(cycle)]['district_held']

            # Source for office(address), phone, fax, website, contact_form, facebook_id, twitter_id ? Not currently known

    # Look up the organizations that donated to this politician

        if sunlight_id is not None:

            if cycle is not None:
                sunlight_pol_url = 'http://transparencydata.com/api/1.0/aggregates/pol/{0}/contributors.json?cycle={1}&apikey={2}'.format(sunlight_id, cycle, sunlight_apikey)
            else:
                sunlight_pol_url = 'http://transparencydata.com/api/1.0/aggregates/pol/{0}/contributors.json?&apikey={1}'.format(sunlight_id, sunlight_apikey)

            try:
                sunlight_contributions_list = json.loads(urllib2.urlopen(sunlight_pol_url).read())
            except urllib2.HTTPError:
                sunlight_contributions_list = []
            
            # Checking whether sunlight_ids for these organizations have been saved in the database yet

            for contribution in sunlight_contributions_list:

                sunlight_contributions_query = "select name, sunlight_id from organizations where name = '{0}'".format(contribution['name'].replace("'","''"))
                database_cursor.execute(sunlight_contributions_query)

                if database_cursor.fetchone() is None: # No rows returned; add name and sunlight_id
                    if contribution['name'] is not None and contribution['id'] is not None:
                        database_cursor.execute("insert into organizations (name, sunlight_id) values ('{0}', '{1}')".format(contribution['name'].replace("'","''"), contribution['id']))
                    elif contribution['name'] is not None and contribution['id'] is None:
                        database_cursor.execute("insert into organizations (name) values ('{0}')".format(contribution['name'].replace("'","''")))
                    database_connection.commit()
                else:
                    try:
                        (org_name, org_sunlight_id) = database_cursor.fetchone()
                    
                        if org_name is not None and org_sunlight_id is not None:
                            continue
                        elif org_name is not None and contribution['name'] is not None and contribution['id'] is not None:
                            database_cursor.execute("update organizations set sunlight_id = '{0}' where name = '{1}'".format(contribution['id'], contribution['name'].replace("'","''")))
                            database_connection.commit()

                    except TypeError, e:
                        if "'NoneType' object is not iterable" in e:
                            pass

            crp_contributions_list = []
            
        else: # Prefer Sunlight's Influence Explorer as it gives more data; use OpenSecrets as backup for contributions

            sunlight_contributions_list = []

            if crp_id is not None:
            
                if cycle is None:
                    crp_contributions_list = CRP.candContrib.get(cid=crp_id)
                else:
                    crp_contributions_list = CRP.candContrib.get(cid=crp_id, cycle=cycle)
            else:
                crp_contributions_list = []

    # Get LittleSis name and id for this politician

        if ((littlesis_id is None and littlesis_name is None) and (bioguide_id is not None or crp_id is not None)):

            if bioguide_id is not None:
                littlesis_lookup_url = 'http://api.littlesis.org/entities/bioguide_id/{0}.json?_key={1}'.format(bioguide_id, littlesis_apikey)

            else: # Prefer bioguide_id, use crp_id as backup

                if crp_id is not None:
                    littlesis_lookup_url = 'http://api.littlesis.org/entities/crp_id/{0}.json?_key={1}'.format(crp_id, littlesis_apikey)

            try:
                littlesis_lookup = json.loads(urllib2.urlopen(littlesis_lookup_url).read())
            except urllib2.HTTPError:
                littlesis_lookup = {}
            
            if len(littlesis_lookup) > 0:
                try:
                    if littlesis_lookup['Data']['Entities'] != '':

                        if littlesis_id is None and littlesis_lookup['Data']['Entities']['Entity']['id'] is not None:
                            database_cursor.execute("update persons set littlesis_id = '{0}' where id = {1}".format(littlesis_lookup['Data']['Entities']['Entity']['id'], person_id))
                            database_connection.commit()
                            littlesis_id = littlesis_lookup['Data']['Entities']['Entity']['id']

                        if littlesis_name is None and littlesis_lookup['Data']['Entities']['Entity']['name'] is not None:
                            database_cursor.execute("update persons set littlesis_name = '{0}' where id = {1}".format(littlesis_lookup['Data']['Entities']['Entity']['name'].replace(" ","_").replace("'","''"), person_id))
                            database_connection.commit()
                            littlesis_name = littlesis_lookup['Data']['Entities']['Entity']['name'].replace(" ","_")
                except KeyError:
                    pass

        if littlesis_id is not None and littlesis_name is not None:                
            littlesis_external_url_politician = "http://littlesis.org/person/{0}/{1}".format(littlesis_id, littlesis_name)
        else:
            littlesis_external_url_politician = 'http://littlesis.org/search?q={0}'.format(person_lastname.replace(" ", "+"))

    # Get Voter Turnout Information

        if cycle is not None:

            if len(sunlight_politician_summary) > 0:
                voter_turnout_query = "select state, vep_turnout_rate from voter_turnout where year = {0} and state_abbrev = '{1}'".format(cycle, sunlight_politician_summary['state'])
            elif len(sunlight_congress_summary) > 0:
                voter_turnout_query = "select state, vep_turnout_rate from voter_turnout where year = {0} and state_abbrev = '{1}'".format(cycle, sunlight_congress_summary['state'])
            else:
                voter_turnout_query = None

            if voter_turnout_query is not None:
                if "state_abbrev = ''" in voter_turnout_query and person_state is not None:
                    voter_turnout_query = voter_turnout_query.replace("state_abbrev = ''", "state_abbrev = '{0}'".format(person_state))
                database_cursor.execute(voter_turnout_query)
                try:
                    (voter_turnout_state, vep_turnout_rate) = database_cursor.fetchone()
                except TypeError:
                    voter_turnout_query = None      

    # Connections

    # Get whether this politician has any position on a bill

        has_position_query = "select bill_id from bill_positions where person_id = {0}".format(person_id)
        database_cursor.execute(has_position_query)

        has_position_on_bills = []
        for has_position in database_cursor.fetchall():
                has_position_on_bills.append(has_position)

    # Check whether those bill positions are opposite to ours and find anyone else who has also taken opposite positions on the same bill(s)

        similar_votes = []
        
        if len(has_position_on_bills) > 0:

            connection_similar_votes_query = """select persons.display_name, bill_positions.position, bills.bill_number, bills.bill_name, quotes.id
            from bill_positions
            inner join bills on bills.id = bill_positions.bill_id
            inner join persons on bill_positions.person_id = persons.id
            inner join quotes on quotes.who_said = persons.id
            where bill_positions.position != our_position
            and bill_positions.position = bills.bad_position
            and bill_positions.position != ''
            and bill_positions.position is not NULL
            where bill_positions.bill_id in ({0}) and persons.id != {1}
            limit 10""".format(', '.join(has_position_on_bills), person_id)
            database_cursor.execute(connection_similar_votes_query)

            for similar_vote in database_cursor.fetchall():
                (other_person_name, other_person_position, other_person_bill_number, other_person_bill_name, other_person_quote_id) = similar_vote
                similar_votes.append('<tr><td>{0} and <a href="quote?quote_id={1}">{2}</a> are both against us on {3} ({4})</td></tr>'.format(person_displayname, other_person_quote_id, other_person_name, other_person_bill_name, other_person_bill_number))
        
    # Get 10 people from the same party

        connection_same_party_query = "select distinct on (persons.id) persons.id, persons.display_name, persons.party, quotes.id from persons inner join quotes on quotes.who_said = persons.id where persons.party = '{0}' and persons.id != {1} and quotes.quote_text != '' limit 10".format(person_party, person_id)
        database_cursor.execute(connection_same_party_query)

        same_party = []
        for similar_party in database_cursor.fetchall():
            (other_person_id, other_person_name, other_person_party, other_person_quote_id) = similar_party
            same_party.append('<tr><td>{0} and <a href="quote?quote_id={1}">{2}</a> are in the {3} party</td></tr>'.format(person_displayname, other_person_quote_id, other_person_name, other_person_party.replace("R", "Republican").replace("D", "Democratic").replace("I", "Independent")))

    # Get other (misc) types of connections, like someone who is a campaign staffer

        has_other_connections_query = "select first_person_id, second_person_id, connection from connections where first_person_id = {0} or second_person_id = {0} limit 10".format(person_id)
        database_cursor.execute(has_other_connections_query)

        other_person_names = {}
        for has_other_connection in database_cursor.fetchall():
            (first_person_id, second_person_id, connection) = has_other_connection
                
            if (first_person_id == person_id): # The person who said the quote of the page we're on is on the "left" side of the connection, example: LEFT is RIGHT's X
                other_person_names[second_person_id] = {'name': None, 'connection': connection, 'side': 'right'}
            else:
                other_person_names[first_person_id] = {'name': None, 'connection': connection, 'side': 'left'}

    # I'm okay with SQL essentially picking a quote at random - I really just want to link to the person's quote page.
        other_connections = []
    
        if len(other_person_names) > 0:
            other_person_names_query = "select persons.id, persons.display_name, quotes.id from persons inner join quotes on quotes.who_said = persons.id where quotes.quote_text != '' and persons.id in ({0})".format(', '.join(other_person_names.keys()))
            database_cursor.execute(other_person_names_query)
                            
            for other_person in database_cursor.fetchall():
                (other_person_id, other_person_name, other_quote_id) = other_person
                other_person_names[other_person_id]['name'] = other_person_name
                other_person_names[other_person_id]['quote'] = other_quote_id

            for other_connection in other_person_names.keys():
                if other_person_names[other_connection]['side'] == 'left': # The other person is on the left side of the sentence
                    other_connections.append("<tr><td><a href='quote?quote_id={0}'>{1}</a> is {2}'s {3}</td></tr>".format(other_person_names[other_connection]['quote'], other_person_names[other_connection]['name'], person_name, other_person_names[other_connection]['connection']))
                else:
                    other_connections.append("<tr><td>{0} is <a href='quote?quote_id={1}'>{2}'s</a> {3}</td></tr>".format(person_name, other_person_names[other_connection]['quote'], other_person_names[other_connection]['name'], other_person_names[other_connection]['connection']))
                
        connections = []

        if (len(similar_votes) + len(same_party) + len(other_connections)) < 10:
            connections.extend(similar_votes)
            connections.extend(same_party)
            connections.extend(other_connections)
        else:
            while len(connections) < 10:  
                if len(similar_votes) > 0:
                    for add_connection in xrange(3): # To attain the ideal ratio of 6 similar votes : 2 same party : 2 other_connections
                        try:
                            connections.append(similar_votes.pop())
                        except IndexError:
                            break
                if len(same_party) > 0:
                    connections.append(same_party.pop())
                if len(other_connections) > 0:
                    connections.append(other_connections.pop())
                

        #   ABOVE: DATA COLLECTION
        #   BELOW: WRITING / FORMATTING
        

    # Build table with attribution and quote

        quote_source = []

        quote_source.append('<table cellpadding=8 style="vertical-align:middle; text-align:center;"><tr><td colspan=2><h2><b>{0}</b></h2></td></tr><tr>'.format(person_displayname))

        try:
            quote_source.append('<td><img alt="{0}" title="{0}" src="{0}"></td>'.format(sunlight_ie_summary['metadata']['photo_url']))
        except KeyError:
            pass

        quote_source.append('<td><h3>"{0}"</h3></td></tr></table><br>&nbsp;<br>'.format(quote_text))

        if len(other_quotes) > 0:
            quote_source.append('<table cellpadding=4 style="vertical-align:middle; text-align:center;"><tr><td>{0}\'s other gems</td></tr>'.format(person_displayname))
            quote_source.extend(other_quotes)
            quote_source.append('</table>')

        quote_source = ''.join(quote_source)

        bio_source = []

        if len(sunlight_congress_summary) > 0:

            if sunlight_congress_summary['party'] == 'R':
                sunlight_politician_party = "<td style='background-color: #ff9999;padding: 6px;'><strong>Republican</strong></td>"
            elif sunlight_congress_summary['party'] == 'D':
                sunlight_politician_party = "<td style='background-color: #9999ff;padding: 6px;'><strong>Democrat</strong></td>"
            else:
                sunlight_politician_party = "<td style='padding: 6px;'<strong>Third party ({0})</strong></td>".format(sunlight_congress_summary['party'])

            if sunlight_congress_summary['in_office'] == True:
                sunlight_politician_current = "<td style='padding: 6px;'><b>In office</b></td>"
            else:
                sunlight_politician_current = "<td style='background-color: #ffccff;padding: 6px;'><strong>Not in office</strong></td>"

            bio_source.append('<table cellpadding=6 style="vertical-align: middle; text-align:center"><tr><td colspan=4>All about <b>{0}</b></td></tr>'.format(person_displayname))

            if sunlight_congress_summary['district'] is None:
                bio_source.append('<tr>{0}<td><b>{1}</b></td><td><b>{2}</b></td>{3}</tr>'.format(sunlight_politician_party, sunlight_congress_summary['state_name'], sunlight_congress_summary['chamber'].capitalize(), sunlight_politician_current))
            else:
                bio_source.append('<tr>{0}<td><b>{1}</b></td><td><b>{2} District {3}</b></td>{4}</tr>'.format(sunlight_politician_party, sunlight_congress_summary['state_name'], sunlight_congress_summary['chamber'].capitalize(), sunlight_congress_summary['district'], sunlight_politician_current))

            if sunlight_congress_summary['in_office'] != True:
                bio_source[-1] = bio_source[-1].replace('<b>','<s><b>').replace('</b>','</b></s>')

        # Build Legislator Summary / Contact Info from Sunlight Congress

            for detail in ['office', 'phone', 'fax', 'website', 'contact_form', 'facebook_id', 'twitter_id']:
                if sunlight_congress_summary[detail] is not None:
                    if detail == 'phone':
                        bio_source.append('<tr><td colspan=4>{0}: <b><a href="tel:{1}" target="_blank">{1}</a></b></td></tr>'.format(detail.replace("_", " ").capitalize(), sunlight_congress_summary[detail]))
                    elif 'http://' in sunlight_congress_summary[detail]:
                        bio_source.append('<tr><td colspan=4>{0}: <b><a href="{1}" target="_blank">{1}</a></b></td></tr>'.format(detail.replace("_", " ").capitalize(), sunlight_congress_summary[detail]))
                    elif detail == 'facebook_id':
                        bio_source.append('<tr><td colspan=2><a href="http://facebook.com/{1}" target="_blank"><img style="vertical-align: middle;" height=33 width=33 src="icons/facebook.png" title="{0}: {1}" alt="{0}: {1}"></a></td><td colspan=2><b><a href="http://facebook.com/{1}" target="_blank">{1}</a></b></td></tr>'.format(detail.replace("_", " ").capitalize().replace(" id", ""), sunlight_congress_summary[detail]))
                    elif detail == 'twitter_id':
                        bio_source.append('<tr><td colspan=2><a href="http://twitter.com/{1}" target="_blank"><img style="vertical-align: middle;" height=33 width=33 src="icons/twitter.png" title="{0}: {1}" alt="{0}: {1}"></a></td><td colspan=2><b><a href="http://twitter.com/{1}" target="_blank">{1}</a></b></td></tr>'.format(detail.replace("_", " ").capitalize().replace(" id", ""), sunlight_congress_summary[detail]))
                    else:
                        bio_source.append('<tr><td colspan=4>{0}: <b>{1}</b></td></tr>'.format(detail.replace("_", " ").capitalize(), sunlight_congress_summary[detail]))
                    if (sunlight_congress_summary['in_office'] != True and detail != 'twitter_id' and detail != 'facebook_id'):
                        bio_source[-1] = bio_source[-1].replace('<b>','<s><b>').replace('</b>','</b></s>').replace("</a>", "").replace('target="_blank">','target="_blank"></a>')

        else: # For politicians who are not members of Congress

            if len(sunlight_politician_summary) > 0:

                if sunlight_politician_summary['party'] == 'R':
                    sunlight_politician_party = "<td style='background-color: #ff9999;padding: 6px;'><strong>Republican</strong></td>"
                elif sunlight_politician_summary['party'] == 'D':
                    sunlight_politician_party = "<td style='background-color: #9999ff;padding: 6px;'><strong>Democrat</strong></td>"
                else:
                    sunlight_politician_party = "<td style='padding: 6px;'<strong>Third party ({0})</strong></td>".format(sunlight_politician_summary['party'])

                if sunlight_politician_summary['in_office'] == True:
                    sunlight_politician_current = "<td style='padding: 6px;'><b>In office</b></td>"
                else:
                    sunlight_politician_current = "<td style='background-color: #ffccff;padding: 6px;'><strong>Not in office</strong></td>"

                bio_source.append('<table cellpadding=6 style="vertical-align: middle; text-align:center"><tr><td colspan=4 style="border: solid 1px;"><h3>All about <b>{0}</b></h3></td></tr>'.format(person_displayname))

                if sunlight_politician_summary['district'] is None:
                    bio_source.append('<tr>{0}<td><b>{1}</b></td><td><b>{2}</b></td>{3}</tr>'.format(sunlight_politician_party, sunlight_politician_summary['state'], sunlight_politician_summary['office'], sunlight_politician_current))
                else:
                    bio_source.append('<tr>{0}<td><b>{1}</b></td><td><b>{2} District {3}</b></td>{4}</tr>'.format(sunlight_politician_party, sunlight_politician_summary['state'], sunlight_politician_summary['office'], sunlight_politician_summary['district'], sunlight_politician_current))

                if sunlight_politician_summary['in_office'] != True:
                    bio_source[-1] = bio_source[-1].replace('<b>','<s><b>').replace('</b>','</b></s>')
            
    # Build Politician External Links: Sunlight, LittleSis, OpenSecrets
        try:
            bio_source.append('<tr><td colspan=2><a href="{0}" target="_blank"><img style="vertical-align: middle;" height=33 width=33 src="icons/sunlight.png" title="View {1} on Sunlight\'s Influence Explorer" alt="View {1} on Sunlight\'s Influence Explorer"></a></td><td colspan=2><b><a href="{0}" target="_blank">View {1} on the Sunlight Foundation\'s Influence Explorer</a></b>\n'.format(sunlight_external_url_politician, person_displayname))
            bio_source.append('</tr><tr><td colspan=2><a href="http://www.opensecrets.org/politicians/summary.php?cid={0}&cycle={1}" target="_blank"><img style="vertical-align: middle; padding:3px;" height=33 width=33 src="icons/opensecrets.png" title="View {2} on Open Secrets" alt="View {2} on Open Secrets"></a></td><td colspan=2><b><a href="http://www.opensecrets.org/politicians/summary.php?cid={0}&cycle={1}" target="_blank">View {2} on Open Secrets</b></a>\n'.format(crp_id, cycle, person_displayname))
            bio_source.append('</tr><tr><td colspan=2><a href="{0}" target="_blank"><img style="vertical-align: middle;" height=33 width=33 src="icons/littlesis.png" title="View {1} on LittleSis" alt="View {1} on LittleSis"></a></td><td colspan=2><b><a href="{0}" target="_blank">View {1} on LittleSis</b></a>\n'.format(littlesis_external_url_politician, person_displayname))
            bio_source.append('</tr><td colspan=4>Politician information provided by the <a href="http://sunlightfoundation.com/" target="_blank">Sunlight Foundation</a></td></tr></table>\n<br>&nbsp;<br>\n\n')
        except UnboundLocalError:
            bio_source.append('</table> <br>')

        bio_source = ''.join(bio_source)

    # Build table with donors

        donors_source = []
    
        if len(sunlight_contributions_list) > 0:

            donors_source.append('<table cellpadding=4 style="vertical-align: middle; text-align: center;"><tr><td colspan=5><b>{0} Donors to <b>{1}</b> (how interesting!)</td></tr>'.format(cycle, person_displayname))
            donors_source.append('<tr><td><b>More Info</b></td><td><b>Donor</b></td><td><b>Total Given</b></td><td><b>Directly Given</b></td><td><b>Given by Employees</b></td></tr>')
            
            for contribution in sunlight_contributions_list: # Sunlight's Influence Explorer breaks donations down by direct vs. employees, which is preferred.

                if contribution['id'] is not None:
                    donors_source.append('<tr><td><a href="http://influenceexplorer.com/organization/{0}/{1}?cycle={2}" target="_blank"><img height=33 width=33 src="icons/sunlight.png" title="View {3} on Sunlight\'s Influence Explorer" alt="View {3} on Sunlight\'s Influence Explorer"></a>\n'.format(contribution['name'].lower().replace('/','').replace(' ','-').replace(' & ',' ').replace('&',''), contribution['id'], cycle, contribution['name']))
                else:
                    donors_source.append('<tr><td>')

                database_cursor.execute("select crp_id, littlesis_id, littlesis_name from organizations where name = '{0}'".format(contribution['name'].replace("'","''")))
                try:
                    (crp_id, littlesis_id, littlesis_name) = database_cursor.fetchone()
                except TypeError, e:
                    if 'NoneType is not iterable' in e:
                        crp_id = littlesis_id = None 

                if crp_id is not None:
                    donors_source.append('<a href="http://www.opensecrets.org/orgs/summary.php?id={0}" target="_blank"><img height=33 width=33 src="icons/opensecrets.png" title="View {1} on Open Secrets" alt="View {1} on Open Secrets"></a>\n'.format(crp_id, contribution['name']))
                
                if littlesis_id is not None and littlesis_name is not None:
                    donors_source.append('<a href="http://littlesis.org/org/{0}/{1}" target="_blank"><img height=33 width=33 src="icons/littlesis.png" title="View {2} on LittleSis" alt="View {2} on LittleSis"></a>\n'.format(littlesis_id, littlesis_name, contribution['name']))
                else:
                    donors_source.append('<a href="http://littlesis.org/search?q={0}" target="_blank"><img height=33 width=33 src="icons/littlesis.png" title="Search for {1} on LittleSis" alt="Search for {1} on LittleSis"></a>\n'.format(contribution['name'].replace(" ", "+"), contribution['name']))

                donors_source.append('</td><td>{0}</td><td>${1:,}</td><td>${2:,}</td><td>${3:,}</td></tr>'.format(contribution['name'], int(float(contribution['total_amount'])), int(float(contribution['direct_amount'])), int(float(contribution['employee_amount']))))

            donors_source.append('<tr><td colspan=5>Donation information provided by the <a href="http://sunlightfoundation.com/" target="_blank">Sunlight Foundation</a>, <a href="http://opensecrets.org/" target="_blank">OpenSecrets.org</a>, and <a href="http://followthemoney.org" target="_blank">FollowTheMoney.org</a></td></tr>')
            
        elif len(crp_contributions_list) > 0:

            donors_source.append('<table cellpadding=4 style="vertical-align: middle; text-align: center;"><tr><td colspan=3>{0} Donors to <b>{1}</b> (how interesting!)</td></tr>'.format(cycle, person_displayname))
            donors_source.append('<tr><td><b>More Info</b></td><td><b>Donor</b></td><td><b>Total Given</b></td></tr>')
            
            for contribution in crp_contributions_list:

                database_cursor.execute("select sunlight_id, crp_id, littlesis_id, littlesis_name from organizations where name = '{0}'".format(contribution['name'].replace("'","''")))
                try:
                    (sunlight_id, crp_id, littlesis_id, littlesis_name) = database_cursor.fetchone()
                except TypeError, e:
                    if 'NoneType is not iterable' in e:
                        sunlight_id = crp_id = littlesis_id = littlesis_name = None
                        donors_source.append('<tr><td>Not available at this time')

                if sunlight_id is not None: # There's no guarantee that CRP will return the precise name that Sunlight's IE expects.  You might not be able to use this, or you might have to look it up anyway.
                    donors_source.append('<tr><td><a href="http://influenceexplorer.com/organization/{0}/{1}?cycle={2}" target="_blank"><img height=33 width=33 src="icons/sunlight.png" title="View {3} on Sunlight\'s Influence Explorer" alt="View {3} on Sunlight\'s Influence Explorer"></a>\n'.format(contribution['@attributes']['org_name'].lower().replace('/','').replace(' ','-').replace(' & ',' ').replace('&',''), sunlight_id, cycle, contribution['@attributes']['org_name']))
                
                if crp_id is not None:
                    donors_source.append('<a href="http://www.opensecrets.org/orgs/summary.php?id={0}" target="_blank"><img height=33 width=33 src="icons/opensecrets.png" title="View {1} on Open Secrets" alt="View {1} on Open Secrets"></a>\n'.format(crp_id, contribution['@attributes']['org_name']))

                if littlesis_id is not None and littlesis_name is not None:
                    donors_source.append('<a href="http://littlesis.org/org/{0}/{1}" target="_blank"><img height=33 width=33 src="icons/littlesis.png" title="View {2} on LittleSis" alt="View {2} on LittleSis"></a>\n'.format(littlesis_id, littlesis_name, contribution['@attributes']['org_name']))
                else:
                    donors_source.append('<a href="http://littlesis.org/search?q={0}" target="_blank"><img height=33 width=33 src="icons/littlesis.png" title="Search for {1} on LittleSis" alt="Search for {1} on LittleSis"></a>\n'.format(contribution['name'].replace(" ", "+"), contribution['name']))

                donors_source.append('</td><td>{0}</td><td>${1:,}</td></tr>'.format(contribution['@attributes']['org_name'], int(float(contribution['@attributes']['total']))))

            donors_source.append('<tr><td colspan=5>Donation information provided by the <a href="http://sunlightfoundation.com/" target="_blank">Sunlight Foundation</a>, <a href="http://opensecrets.org/" target="_blank">OpenSecrets.org</a>, and <a href="http://followthemoney.org" target="_blank">FollowTheMoney.org</a></td></tr>')
            
        donors_source.append('</table>\n<br>&nbsp;<br>\n\n')

        donors_source = ''.join(donors_source)

    # Build Voter Turnout / Voter Registration table

        turnout_source = []

        if voter_turnout_query is not None and cycle is not None: 

            rockthevote_embedcode = """<a href="https://register2.rockthevote.com/?partner=24853&source=embed-rtv234x60v1" class="floatbox" data-fb-options="width:618 height:max scrolling:yes">
<img src="http://register.rockthevote.com/images/widget/rtv-234x60-v1.gif" /></a><script type="text/javascript" src="https://register2.rockthevote.com/widget_loader.js"></script>"""

            turnout_source.append('<table cellpadding=4 style="vertical-align: middle; text-align: center;"><tr><td>In {0}, turnout among eligible voters was only {1:0.4}% in {2}! We can do better! Register to vote here: </td></tr>'.format(cycle, vep_turnout_rate*100, voter_turnout_state))
            turnout_source.append('<tr><td>{0}</td></tr></table>\n<br>&nbsp;<br>\n\n'.format(rockthevote_embedcode))

        turnout_source = ''.join(turnout_source)                                      

    # Build Connections table

        connections_source = []

        if len(connections) > 0:
            connections_source.append('<table cellpadding=4 style="vertical-align:middle; text-align:center;"><tr><td><h3>{0}\'s Connections</h3></td></tr>'.format(person_displayname))

            for connection in connections:
                connections_source.append('<tr><td>{0}</td></tr>'.format(connection))
            connections_source.append('</table>')

        connections_source = ''.join(connections_source)                

    # Now join all pieces together

        page_source.append('<div class="row"> <div class="small-12 small-centered columns"> {0} </div> </div>'.format(quote_source))
        page_source.append('<div class="row"> <div class="small-4 columns"> {0} </div>'.format(bio_source))
        page_source.append('<div class="small-6 columns"> {0} </div> </div>'.format(connections_source))
        page_source.append('<div class="row"> <div class="small-4 columns"> {0} </div> </div>'.format(turnout_source))
        page_source.append('<div class="row"> <div class="small-10 small-centered columns"> {0} </div> </div>'.format(donors_source))         

    elif person_type == 2: # Media figure

        quote_source = []

        quote_source.append('<table cellpadding=8 style="vertical-align:middle; text-align:center;"><tr><td colspan=2><h2><b>{0}</b></h2></td></tr><tr>'.format(person_displayname))
        quote_source.append('<td><h3>"{0}"</h3></td></tr></table><br>&nbsp;<br>'.format(quote_text))

        if len(other_quotes) > 0:
            quote_source.append('<table cellpadding=4 style="vertical-align:middle; text-align:center;"><tr><td>{0}\'s other gems</td></tr>'.format(person_displayname))
            quote_source.extend(other_quotes)
            quote_source.append('</table><br>')

        quote_source = ''.join(quote_source)

        page_source.append('<div class="row"> <div class="small-12 small-centered columns">')
        page_source.extend(quote_source)
        page_source.append('</div> </div> <div class="row"> <div class="small-8 small-centered columns">')
        page_source.append('<table cellpadding=8 style="vertical-align:middle; text-align:center;"><tr><td><h2>Advertisers, take note: <br> Do you really want to be associated with this?</h2></td></tr>')
        page_source.append('<tr><td><i>Ideally, we would like to display the current advertisers supporting {0}.  Unfortunately, we have been unable to identify a source for this information.  <br>&nbsp;<br><b>If you know where we could find this, please send an email to <a href="mailto:adzdata@shutthatdown.com">adzdata@shutthatdown.com</a></b> - just be sure to remove the Z from the email address before you send (it\'s an anti-spam measure).</i></td></tr>'.format(person_displayname))
        page_source.append('</table> </div> </div>')

    elif person_type == 3: # Other public figure

        has_other_connections_query = "select first_person_id, second_person_id, connection from connections where first_person_id = {0} or second_person_id = {0} limit 10".format(person_id)
        database_cursor.execute(has_other_connections_query)

        other_person_names = {}
        for has_other_connection in database_cursor.fetchall():
            (first_person_id, second_person_id, connection) = has_other_connection
                
            if (first_person_id == person_id): # The person who said the quote of the page we're on is on the "left" side of the connection, example: LEFT is RIGHT's X
                other_person_names[second_person_id] = {'name': None, 'connection': connection, 'side': 'right'}
            else:
                other_person_names[first_person_id] = {'name': None, 'connection': connection, 'side': 'left'}

    # I'm okay with SQL essentially picking a quote at random - I really just want to link to the person's quote page.
        other_connections = []
    
        if len(other_person_names) > 0:
            other_person_names_query = "select persons.id, persons.display_name, quotes.id from persons inner join quotes on quotes.who_said = persons.id where quotes.quote_text != '' and persons.id in ({0})".format(', '.join(other_person_names.keys()))
            database_cursor.execute(other_person_names_query)
                            
            for other_person in database_cursor.fetchall():
                (other_person_id, other_person_name, other_quote_id) = other_person
                other_person_names[other_person_id]['name'] = other_person_name
                other_person_names[other_person_id]['quote'] = other_quote_id

            for other_connection in other_person_names.keys():
                if other_person_names[other_connection]['side'] == 'left': # The other person is on the left side of the sentence
                    other_connections.append("<tr><td><a href='quote?quote_id={0}'>{1}</a> is {2}'s {3}</td></tr>".format(other_person_names[other_connection]['quote'], other_person_names[other_connection]['name'], person_name, other_person_names[other_connection]['connection']))
                else:
                    other_connections.append("<tr><td>{0} is <a href='quote?quote_id={1}'>{2}'s</a> {3}</td></tr>".format(person_name, other_person_names[other_connection]['quote'], other_person_names[other_connection]['name'], other_person_names[other_connection]['connection']))
        
        quote_source = []

        quote_source.append('<table cellpadding=8 style="vertical-align:middle; text-align:center;"><tr><td colspan=2><h2><b>{0}</b></h2></td></tr><tr>'.format(person_displayname))
        quote_source.append('<td><h3>"{0}"</h3></td></tr></table><br>&nbsp;<br>'.format(quote_text))

        if len(other_quotes) > 0:
            quote_source.append('<table cellpadding=4 style="vertical-align:middle; text-align:center;"><tr><td>{0}\'s other gems</td></tr>'.format(person_displayname))
            quote_source.extend(other_quotes)
            quote_source.append('</table><br>')

        littlesis_source = []

        littlesis_source.append('<table cellpadding=8 style="vertical-align:middle; text-align:center;"><tr><td><b><a href="http://littlesis.org/search?q={0}" target="_blank">Search for {1}\'s connections on LittleSis</a></b></td></tr>'.format(person_lastname.replace(" ", "+"), person_displayname))
        littlesis_source.append('</table>')

        # Build Connections table

        connections_source = []

        if len(other_connections) > 0:
            connections_source.append('<table cellpadding=4 style="vertical-align:middle; text-align:center;"><tr><td><h3>{0}\'s Connections</h3></td></tr>'.format(person_displayname))
            connections_source.extend(other_connections)
            connections_source.append('</table>')

        page_source.append('<div class="row"> <div class="small-12 small-centered columns">')
        page_source.extend(quote_source)
        page_source.append('</div></div>')

        page_source.append('<div class="row"> <div class="small-6 small-centered columns">')
        page_source.extend(littlesis_source)
        page_source.append('</div></div>')

        page_source.append('<div class="row"> <div class="small-8 small-centered columns">')
        page_source.extend(connections_source)
        page_source.append('</div></div>')

    database_cursor.close()

    return wrap_in_css(page_source, '{0}'.format(person_displayname))
