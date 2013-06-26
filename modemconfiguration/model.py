import locale
import logging
import os.path
from xml.etree.cElementTree import ElementTree

from gi.repository import Gtk

from .config import COUNTRY_CODES_PATH, PROVIDERS_PATH, PROVIDERS_FORMAT_SUPPORTED
# from .config import GSM_COUNTRY_PATH, GSM_PROVIDERS_PATH, GSM_PLAN_PATH


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


class DatabaseError(Exception):
    pass


class Country(object):
    def __init__(self, idx, code, name):
        self.idx = idx
        self.code = code
        self.name = name


class Provider(object):
    def __init__(self, idx, name):
        self.idx = idx
        self.name = name


class Plan(object):
    DEFAULT_NUMBER = '*99#'

    def __init__(self, idx, name, apn, username=None, password=None, number=None):
        self.idx = idx
        self.name = name
        self.apn = apn
        self.username = username or ''
        self.password = password or ''
        self.number = number or self.DEFAULT_NUMBER


class ServiceProvidersDatabase(object):
    def __init__(self):
        # Check ISO 3166 alpha-2 country code file exists
        if not os.path.isfile(COUNTRY_CODES_PATH):
            msg = ("Mobile broadband provider database: Country "
                   "codes path %s not found.") % COUNTRY_CODES_PATH
            logging.warning(msg)
            raise DatabaseError(msg)

        # Check service provider database file exists
        try:
            tree = ElementTree(file=PROVIDERS_PATH)
        except (IOError, SyntaxError), e:
            msg = ("Mobile broadband provider database: Could not read "
                   "provider information %s error=%s") % (PROVIDERS_PATH, e)
            logging.warning(msg)
            raise DatabaseError(msg)

        # Check service provider da
        self.root = tree.getroot()
        if self.root.get('format') != PROVIDERS_FORMAT_SUPPORTED:
            msg = ("Mobile broadband provider database: Could not "
                   "read provider information. Wrong format.")
            logging.warning(msg)
            raise DatabaseError(msg)

        language_code = locale.getdefaultlocale()[0]
        self.COUNTRY_CODE = language_code[3:5].lower()
        self.LANG = language_code[0:2]
        self.LANG_NS_ATTR = '{http://www.w3.org/XML/1998/namespace}lang'

        # Load country code label mapping
        codes = {}
        with open(COUNTRY_CODES_PATH) as codes_file:
            for line in codes_file:
                if line.startswith('#'):
                    continue
                code, name = line.split('\t')[:2]
                codes[code.lower()] = name.strip()

        # Populate countries list
        self.countries = []
        for idx, country in enumerate(self.root.iter('country')):
            country_code = country.attrib['code']
            country = Country(idx, country_code, codes[country_code])
            self.countries.append(country)

        # FIXME: Use value persisted in GConf or guess using locale
        self.set_country(self.COUNTRY_CODE)
        # FIXME: Use value persisted in GConf or first
        self.set_provider(0)
        # FIXME: Use value persisted in GConf or first
        self.set_plan(0)


    def set_country(self, country_code):
        self._current_country = country_code
        self._update_providers()

    def set_provider(self, idx):
        self._current_provider = idx
        self._update_plans()

    def set_plan(self, idx):
        self._current_plan = idx

    def _get_country_element(self):
        return self.root.find('country[@code="%s"]' % self._current_country)

    def _get_providers_elements(self):
        return self._get_country_element().findall('provider')

    def _get_provider_element(self):
        idx = self._current_provider
        # Warning! XPath index begins with 1
        return self._get_country_element().find('.//provider[%s]'
                                                % (int(idx) + 1))

    def _get_plan_elements(self):
        return self._get_provider_element().findall('.//apn')

    def _get_localized_or_default_name(self, el):
        tag = el.find('name[@%s="%s"]' % (self.LANG_NS_ATTR, self.LANG))
        if tag is not None:
            return tag
        return el.find('name')

    def get_countries(self):
        return self.countries

    def _update_providers(self):
        self._providers = []
        for idx, provider_el in enumerate(self._get_providers_elements()):
            name_tag = self._get_localized_or_default_name(provider_el)
            name = name_tag.text
            provider = Provider(idx, name)
            self._providers.append(provider)
        return self._providers

    def get_providers(self):
        return self._providers

    def _update_plans(self):
        self._plans = []
        for idx, apn_el in enumerate(self._get_plan_elements()):
            name_tag = self._get_localized_or_default_name(apn_el)
            username_tag = apn_el.find('username')
            password_tag = apn_el.find('password')
            plan = {
                'apn': apn_el.get('value'),
                'name': name_tag.text if name_tag is not None else None,
                'username': username_tag.text if username_tag is not None else None,
                'password': password_tag.text if password_tag is not None else None,
            }
            self._plans.append(Plan(idx, **plan))
        return self._plans

    def get_plans(self):
        return self._plans

    def get_settings(self):
        pass


class Plan2(list):
    @property
    def apn(self):
        return "www.example.com"

class Provider2(object):
    def __init__(self, name):
        self.name = name

    @property
    def plans(self):
        plan_store = Gtk.ListStore(str, object)
        for plan in plans[self.name]:
            plan_store.append([plan, Plan(plan)])
        return plan_store

class Country2(object):
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

# countries = [
#     Country("Austria"),
#     Country("Brazil"),
#     Country("Belgium"),
# ]

# class CountryListStore(Gtk.ListStore):
#     def __init__(self, *args, **kwargs):
#         Gtk.ListStore.__init__(self, str, object)
#         for country in countries:
#             self.append([country.name, country])
