def tag_quote(self, **kwargs):

    from shutthatdown_admin import wrap_in_css
    from shutthatdown_admincredentials import database_connection_details
    import psycopg2

    database_connection = psycopg2.connect(database_connection_details)
    database_cursor = database_connection.cursor()

    who_said = kwargs.get('who_said')
    issue = kwargs.get('issue')
    quote_id = kwargs.get('quote_id')

    if who_said is not None and issue is not None and quote_id is not None:

        try:
            who_said = int(who_said)               
            quote_id = int(quote_id)
        except ValueError:
            pass
        else:
            database_cursor.execute("update quotes set who_said = '{0}' where id = {1}".format(who_said, quote_id))
            
        for issue_id in issue:
            try:
                issue = int(issue)
                database_cursor.execute("insert into quote_issues (quote_id, issue_id) values ('{0}', '{1}')".format(quote_id, issue_id))
            except ValueError:
                break
        else:
            database_connection.commit()                                    

    del kwargs

    page_source = []

    who_said_query = "select persons.id, persons.display_name from persons order by persons.last_name"
    database_cursor.execute(who_said_query)

    who_said_choices = []
    who_said_selector = []
    who_said_selector.append('<td><select name="who_said"><option value="">--------------------------------</option>\n')
    
    for (who_said_id, who_said) in database_cursor.fetchall():
        who_said_choices.append(who_said)
        who_said_selector.append('<option value="{0}">{1}</option>\n'.format(who_said_id, who_said))
    who_said_selector.append('</select></td>')

    issues_query = "select issues.id, issues.issue from issues"
    database_cursor.execute(issues_query)

    issues_choices = []
    issues_selector = []
    for (issue_choice_id, issue_choice) in database_cursor.fetchall():
        issues_choices.append(issue_choice)
        issues_selector.append('<td><input type=checkbox name="issue" value="{0}">{1}</td>'.format(issue_choice_id, issue_choice))

    gather_quotes = []
    gather_quotes_query = "select quotes.id, quotes.quote_text, quotes.who_said from quotes where (id not in (select quote_issues.quote_id from quote_issues)) or (quotes.who_said is NULL) limit 1"
    database_cursor.execute(gather_quotes_query)

    # TODO: Add handling for if who_said exists already
    for (gathered_quote_id, gathered_quote_text, gathered_who_said) in database_cursor.fetchall():
        gather_quotes.append("<tr><td>{0}</td>".format(gathered_quote_text))
        gather_quotes.append('<input type="hidden" name="quote_id" value="{0}">'.format(gathered_quote_id))
        gather_quotes.extend(who_said_selector)
        gather_quotes.extend(issues_selector)
        gather_quotes.append("</tr>")

    database_connection.close()

    page_source.append('<div class="row"> <div class="small-12 small-centered columns">')
    page_source.append("<h2>Tag Quotes with Who Said and Issues</h2>")
    page_source.append('<table cellpadding=4 style="vertical-align: middle; text-align: center; border: 0px;"> <form method=post action=tag_quote>')
    page_source.extend(gather_quotes)
    page_source.append('</table> <br> <input type="submit"> </form>  </div> </div>')

    return wrap_in_css(page_source, "Tag Quote")
