
def about(self, **kwargs):

    """ shutthatdown.com/about
    """

    del kwargs

    page_source = []

    page_source.append('<div class="row"> <div class="small-8 small-centered columns"> <table cellpadding=4 style="vertical-align: middle; text-align: center;">')

    page_source.append('<tr><td><h3>Shut That Down</h3> is a central repository of misogynist, racist, xenophobic, homophobic, and transphobic comments made by politicians, media figures, and other public figures.</td></tr>')
    page_source.append('<tr><td>Our goal is to make sure politicians and media figures can\'t get away with misogyny, racism, xenophobia, homophobia, and transphobia.</td></tr>')
    page_source.append('<tr><td>We aim to educate the public on who is spouting hatred -- and what corporations are funding that hatred through campaign contributions and advertiser dollars.</td></tr>')
    page_source.append('<tr><td><h3>See who\'s funding hate in your state.</h3><br><h3><b>Then SHUT THAT DOWN</b></h3></td></tr>')

    page_source.append('<tr><td>&nbsp;</td></tr>')

    page_source.append('<tr><td><h6>As an anti-spam measure, we have added a Z to each email address below.  Humans, remove the Z before you send.</h6></td></tr>')
    page_source.append('<tr><td>Feedback / General questions: <a href="mailto:inzfo@shutthatdown.com">inzfo@shutthatdown.com</a><br>')
    page_source.append('<tr><td>Media: <a href="mailto:medzia@shutthatdown.com">medzia@shutthatdown.com</a><br>')
    page_source.append('<tr><td>Send new or missing quotes and/or bills here, and be sure to include a link for your source: <a href="mailto:newqzuote@shutthatdown.com">newqzuote@shutthatdown.com</a><br>')
    page_source.append('<tr><td>We do our best to source quotes as they\'re written or spoken, in the appropriate context, and if necessary, with an appropriate explanation.  If we have made a mistake however, we regret the error and strive for accuracy.  Send corrections to: <a href="mailto:miszquote@shutthatdown.com">miszquote@shutthatdown.com</a><br>')

    page_source.append('<tr><td>&nbsp;</td></tr>')

    page_source.append('<tr><td><b>Some notes on how Shut That Down tags certain quotes:</b></td></tr>')
    page_source.append("<tr><td>&bullet; Taking away women's agency, especially in regard to their bodily autonomy, is misogyny.</td></tr>")
    page_source.append("<tr><td>&bullet; Rape apology, denial, and victim blaming, is misogyny.</td></tr>")
    page_source.append('<tr><td>&bullet; Much of transphobia is rooted in transmisogyny.</td></tr>')
    page_source.append('<tr><td>&bullet; Many xenophobic quotes are racist in nature.</td></tr>')
    page_source.append('</td></tr>')
    
    page_source.append('</table> </div></div>')

    return wrap_in_css(page_source, 'About Shut That Down')
