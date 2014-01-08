def error_page(self, **kwargs):

    """ Cherrypy.Root.error_page(): Redirects any page that would fail to /index; if that fails, returns an error message.
    """

    error_message = kwargs.get('error_message')
    del kwargs
    
    try:
        if error_message is None:
            error_message = 'There was an error processing your request.  Please try again.  If this is a recurring issue, please notify our development team at <a href="mailto:inzfo@shutthatdown.com" target="_blank">inzfo@shutthatdown.com</a> -- be sure to remove the Z. '
        error_message = {'error_message': error_message}
        return self.index(**error_message)
    except Exception:
        return wrap_in_css(['<div class="row"> <div class="small-centered small-4 columns">Oops! Did you find a bug in our code? Our development team has been notified. Thanks!</div> </div>'], "Oh no!")
