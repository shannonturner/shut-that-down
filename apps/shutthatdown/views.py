from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from apps.shutthatdown.models import Quote, QuoteType, Person, Contributor
from localflavor.us.us_states import US_STATES

import random
import requests
import time

def get_contributions(sunlight_ie_url):

    try:
        response = requests.get(sunlight_ie_url).json()
    except:
        return 'Error: Could not look up contribution information for this politician. Sorry!'
    else:
        return parse_contributions(response)

def parse_contributions(response):

    ' Parse campaign contributions returned by the Influence Explorer API '

    contributions = []

    for contribution in response:
        try:
            amount = int(float(contribution.get('direct_amount', 0)))

            if amount > 0 and contribution.get('name'):
                contributions.append({
                        'name': contribution.get('name'),
                        'amount': '{:,}'.format(amount),
                    })

                # Look up Contributor; add if new
                try:
                    contributor = Contributor.objects.get(name=contribution.get('name'))
                except ObjectDoesNotExist:
                    new_contributor = Contributor(name=contribution.get('name'))
                    new_contributor.save()
                else:
                    if contributor.errata:
                        contributions[-1]['errata'] = contributor.errata
                    if contributor.facebook:
                        contributions[-1]['facebook'] = contributor.facebook
                    if contributor.twitter:
                        contributions[-1]['twitter'] = contributor.twitter
                    if contributor.email:
                        contributions[-1]['email'] = contributor.email
        except:
            pass

    return contributions

class HomeView(TemplateView):

    template_name = 'index.html'

    def get(self, request, **kwargs):
        return render(request, self.template_name, {})

class QuoteView(TemplateView):

    template_name = 'quote.html'

    def get(self, request, **kwargs):

        quote = kwargs.get('quote')

        try:
            quote = int(quote)
            quote = Quote.objects.get(id=quote)
        except:
            quote = random.randint(1, Quote.objects.count())
            return HttpResponseRedirect('/quote/{0}'.format(quote))

        context = self.get_context_data(**{
            'who': quote.who.id,
            'quote': quote,
            })

        context['quote'] = quote

        if context.get('error'):
            messages.error(request, context['error'])

        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):

        who = kwargs.get('who')
        quote = kwargs.get('quote')

        cycle = time.gmtime()[0] # Current year

        context = {}

        try:
            person = Person.objects.get(id=who)
        except ObjectDoesNotExist:
            context['error'] = 'Error: Could not look up person who said this quote. This should never happen.'
        # else:
            # from .credentials import SUNLIGHT_APIKEY

            # if person.sunlight:
            #     sunlight_ie_url = 'http://transparencydata.com/api/1.0/aggregates/pol/{0}/contributors.json?cycle={1}&apikey={2}'.format(person.sunlight, cycle, SUNLIGHT_APIKEY)
            #     contributions = get_contributions(sunlight_ie_url)

            #     if 'Error' in contributions:
            #         context['error'] = contributions
            #         contributions = ''
            #     else:
            #         if len(contributions) == 0:
            #             sunlight_ie_url = 'http://transparencydata.com/api/1.0/aggregates/pol/{0}/contributors.json?&apikey={1}'.format(person.sunlight, SUNLIGHT_APIKEY)
            #             contributions = get_contributions(sunlight_ie_url)

        # context['contributions'] = contributions
        context['contributions'] = []
        context['person'] = person
        other_quotes = Quote.objects.exclude(id=quote.id)
        context['other_quotes'] = random.sample(other_quotes, 3)

        return context

class StateView(TemplateView):

    template_name = 'state.html'

    def get(self, request, **kwargs):

        state = kwargs.get('state')
        context = {}

        try:
            valid_states = US_STATES
            states_dict = {abbrev: name for abbrev, name in US_STATES}
            if state.upper() not in [valid_state[0] for valid_state in valid_states]:
                raise ValueError
        except:
            if state:
                messages.error(request, 'Invalid state {0} - please try again'.format(state))
        else:
            context = self.get_context_data(**{
                    'state': state,
                })
            try:
                if len(context['quotes']) == 0:
                    messages.warning(request, '''No quotes found for {0}. 
                        If you know of a quote that's missing, please 
                        <b><a href="/submit">submit one!</a></b>'''.format(
                            states_dict[state.upper()]))
                else:
                    messages.info(request, '<b>{0} quotes found for {1}</b>'.format(
                        len(context['quotes']), states_dict[state.upper()]))
            except:
                pass

        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):

        state = kwargs.get('state')

        quotes = Quote.objects.filter(who__state=state.upper())

        context = {
            'state': state,
            'quotes': quotes,
        }

        return context

class BrowseView(TemplateView):

    template_name = 'browse.html'

    def get(self, request, **kwargs):

        quote_type = kwargs.get('type')
        try:
            quote_type = QuoteType.objects.get(quote_type__iexact=quote_type)
        except:
            return HttpResponseRedirect('/')
        else:
            context = self.get_context_data(**{
                    'quote_type': quote_type
                })

        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):

        quote_type = kwargs.get('quote_type')

        quotes = Quote.objects.filter(types=quote_type)

        context = {
            'quotes': quotes,
            'quote_type': quote_type,
        }

        return context

class SubmitView(TemplateView):

    template_name = 'submit.html'

    def get(self, request, **kwargs):
        return render(request, self.template_name, {})