def index(self, **kwargs):

	"Admin panel of Shut That Down"

	from wrap_in_css import wrap_in_css

	warning_ = """<h2>It's important to run this locally on your machine.  If you run the administation panel on your webserver, you MUST secure it.  Anyone with access to this page can make changes to your database!</h2>"""

	return wrap_in_css(warning_, "Shut That Down ADMIN Panel")