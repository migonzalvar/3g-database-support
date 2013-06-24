from gi.repository import Gtk

from .config import GSM_COUNTRY_PATH, GSM_PROVIDERS_PATH, GSM_PLAN_PATH


def get_initial_rows():
    return 2, 1, 0


def get_initial_country():
    # Check if persisted throw GConf GSM_COUNTRY_PATH
    # If not guess using locale.getdefaultlocale()[0][3:5].lower()
    return 2


def get_initial_provider():
    # Check if persisted throw GConf GSM_PROVIDERS_PATH
    return 1


def get_initial_plan():
    # Check if persisted throw GConf GSM_PLAN_PATH
    return 0


class Plan(list):
    @property
    def apn(self):
        return "www.example.com"

class Provider(object):
    def __init__(self, name):
        self.name = name

    @property
    def plans(self):
        plan_store = Gtk.ListStore(str, object)
        for plan in plans[self.name]:
            plan_store.append([plan, Plan(plan)])
        return plan_store

class Country(object):
    def __init__(self, name):
        self.name = name

    @property
    def providers(self):
        provider_store = Gtk.ListStore(str, object)
        for provider in providers[self.name]:
            provider_store.append([provider, Provider(provider)])
        return provider_store

plans = {
    'Aaa': ['morning', 'afternoon'],
    'Bbb': ['S', 'XL'],
    'Zzz': ['base', 'red'],
    'Yyy': ['combo', 'multi'],
    '123': ['prepaid', 'postpaid'],
    '987': ['basic', 'premium'],
}

providers = {
    "Austria": ["Aaa", "Bbb"],
    "Brazil": ["Zzz", "Yyy"],
    "Belgium": ["123", "987"],
}

countries = [
    Country("Austria"),
    Country("Brazil"),
    Country("Belgium"),
]

class CountryListStore(Gtk.ListStore):
    def __init__(self, *args, **kwargs):
        Gtk.ListStore.__init__(self, str, object)
        for country in countries:
            self.append([country.name, country])


