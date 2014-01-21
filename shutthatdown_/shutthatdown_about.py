def about(self, **kwargs):

    """ shutthatdown.com/about
    """

    del kwargs

    from shutthatdown_ import shutthatdown_wrapincss
    wrap_in_css = shutthatdown_wrapincss.wrap_in_css

    with open('static/about.html') as static_about:
        page_source = static_about.read()

    return wrap_in_css(page_source, 'About Shut That Down')
