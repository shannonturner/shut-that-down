from django.contrib import admin
from apps.shutthatdown.models import Person, QuoteType, Quote, Contributor

admin.site.register(Person)
admin.site.register(QuoteType)
admin.site.register(Quote)
admin.site.register(Contributor)