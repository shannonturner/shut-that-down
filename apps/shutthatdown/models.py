from django.db import models
from localflavor.us.models import USStateField

class Person(models.Model):

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=255)

    image_url = models.CharField(max_length=255, null=True, blank=True)

    title = models.CharField(max_length=255, null=True, blank=True)
    state = USStateField(null=True, blank=True)
    party = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=100, null=True, blank=True)

    facebook = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    influence_explorer = models.CharField(max_length=255, null=True, blank=True)

    sunlight = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return self.display_name

class QuoteType(models.Model):

    quote_type = models.CharField(max_length=100)

    def __unicode__(self):
        return self.quote_type

class Quote(models.Model):

    quote = models.TextField()
    who = models.ForeignKey(Person, related_name='who')
    source_url = models.CharField(max_length=255)
    types = models.ManyToManyField(QuoteType, related_name='types')

    def __unicode__(self):
        return self.quote[:10]

class Contributor(models.Model):

    ' A company or group that has given a political contribution '

    name = models.CharField(max_length=255)

    facebook = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.name