def newquote(self, **kwargs):

    from shutthatdown_admin import wrap_in_css
    from shutthatdown_admincredentials import database_connection_details
    import psycopg2

    page_source = []

    database_connection = psycopg2.connect(database_connection_details)
    database_cursor = database_connection.cursor()

    database_cursor.execute("select persons.id, persons.display_name from persons")

    all_persons = []
    all_valid_ids = []
    for who_said in database_cursor.fetchall():
        all_persons.append(who_said)
        all_valid_ids.append(who_said[0])

    try:

        if kwargs['quotetext'] != '' and kwargs['who_said'] != '' and kwargs['issues'] != '':

            try:
                who_said = int(kwargs['who_said'])
                if who_said not in all_valid_ids:
                    who_said = None
            except ValueError:
                who_said = None
            except TypeError:
                who_said = None

            issues = kwargs['issues']
            quote_text = kwargs['quotetext']
            del kwargs
                
            database_cursor.execute("INSERT INTO quotes (quote_text, who_said) VALUES ('{0}', '{1}') RETURNING id".format(quote_text, who_said))
            quote_id = database_cursor.fetchone()[0] # Get the quote_id for the row I just inserted
            database_cursor.commit()

            for issue in issues:
                try:
                    issue = int(issue)
                    if issue not in (1,2,3,4):
                        issue = None
                except ValueError:
                    issue = None
                except TypeError:
                    issue = None

                if issue is not None:
                    database_cursor.execute("INSERT INTO quote_issues (quote_id, issue_id) VALUES ('{0}', '{1}')".format(quote_id, issue))

            database_cursor.commit()

    except KeyError:
        pass      

    # Always write out the form so another quote can be added right away

    page_source.append('<div class="row"> <div class="small-6 small-centered columns">')

    page_source.append('<table cellpadding=4 style="vertical-align: middle; text-align: center; border: 0px;"><tr><td><h2>ADMIN - ADD NEW QUOTE</h2></td></tr></table> </div></div>')

    page_source.append('<div class="row"> <div class="small-8 small-centered columns">')

    page_source.append('<form id="newquote" name="newquote" method="post" action="newquote">')

    page_source.append('<fieldset id="quotetext"><legend><h3>Quote Text</h3></legend>')
    page_source.append('<textarea name="quotetext" id="quotetext" rows=10 cols=20></textarea>')
    page_source.append('</fieldset>')

    page_source.append('<fieldset id="whosaid"><legend><h3>Who Said</h3></legend>')

    page_source.append('<select name="who_said">')
    page_source.append('<option value=""> </option>')
    for who_said in all_persons:
        (person_id, person_displayname) = who_said
        page_source.append('<option value="{0}">{1}</option>'.format(person_id, person_displayname))
    page_source.append('</select>')
        
    page_source.append('</fieldset>')

    page_source.append('<fieldset id="issues"><legend><h4>Issues</h4></legend>')
    page_source.append('<table cellpadding=4 style="vertical-align: middle; text-align: center; border: 0px;">')
    page_source.append('<tr><td><input type="checkbox" name="issues" value="1">Misogynist</td></tr>')
    page_source.append('<tr><td><input type="checkbox" name="issues" value="2">Racist</td></tr>')
    page_source.append('<tr><td><input type="checkbox" name="issues" value="3">Xenophobic</td></tr>')
    page_source.append('<tr><td><input type="checkbox" name="issues" value="4">Homophobic or Transphobic</td></tr>')
    page_source.append('</table></fieldset>')                                            

    page_source.append('<input type="submit" class="button" value="Add Quote"></form> </div></div>')

    database_connection.close()        

    return wrap_in_css(page_source, "Add New Quote")
