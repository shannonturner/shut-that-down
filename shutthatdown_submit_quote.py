def submit_quote(self, **kwargs):

    """ Cherrypy.Root.submit_quote(): shutthatdown.com/submit_quote (Hooks into Google Form)
    """

    del kwargs

    page_source = []

    page_source.append('<div class="row"> <div class="small-8 small-centered columns">')
    page_source.append('<iframe src="https://docs.google.com/forms/d/1xzyx_9maLkASiShXwvzPe8VIQpXstSSRIJVRgHg2hps/viewform?embedded=true" width="760" height="660" frameborder="0" marginheight="0" marginwidth="0">Loading...</iframe>')
    page_source.append('</div> </div>')

    return wrap_in_css(page_source, "Submit new quote")
