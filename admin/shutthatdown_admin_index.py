def index(self, **kwargs):

    from shutthatdown_admin import wrap_in_css

    page_source = """<h3> Welcome to the Shut That Down Admin Panel! <br>

    To make things look pretty, copy your css and js directories to this folder.<br>

    If you have not already done so, please <br>

    TAKE APPROPRIATE MEASURES TO SECURE YOUR ADMIN PANEL. <br>

    ANYONE WITH ACCESS TO THIS PAGE CAN MAKE SIGNIFICANT CHANGES TO YOUR DATABASE.</h3>"""

    return wrap_in_css(page_source, "Admin - Shut That Down")
