# -*- encoding: utf-8 -*-
# Copyright (C) 2010 Andrés Ambrois
# Copyright (C) 2012 Ajay Garg
# Copyright (C) 2013 Miguel González
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

import locale
import logging
import os.path
from xml.etree.cElementTree import ElementTree
from gettext import gettext as _

from gi.repository import GConf

from .config import COUNTRY_CODES_PATH, PROVIDERS_PATH, PROVIDERS_FORMAT_SUPPORTED
from .config import GCONF_SP_COUNTRY, GCONF_SP_PROVIDER, GCONF_SP_PLAN


class ServiceProviderDatabaseError(Exception):
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
            raise ServiceProviderDatabaseError(msg)

        # Check service provider database file exists
        try:
            tree = ElementTree(file=PROVIDERS_PATH)
        except (IOError, SyntaxError), e:
            msg = ("Mobile broadband provider database: Could not read "
                   "provider information %s error=%s") % (PROVIDERS_PATH, e)
            logging.warning(msg)
            raise ServiceProviderDatabaseError(msg)

        # Check service provider da
        self.root = tree.getroot()
        if self.root.get('format') != PROVIDERS_FORMAT_SUPPORTED:
            msg = ("Mobile broadband provider database: Could not "
                   "read provider information. Wrong format.")
            logging.warning(msg)
            raise ServiceProviderDatabaseError(msg)

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
        self._countries, self._current_country = [], 0
        country_codes = []
        for idx, country in enumerate(self.root.iter('country')):
            country_code = country.attrib['code']
            country = Country(idx, country_code, codes[country_code])
            self._countries.append(country)
            country_codes.append(country_code)

        country_code, provider_idx, plan_idx = self._get_initials()
        country_idx = country_codes.index(country_code)
        self.set_country(country_idx)
        self._providers, self._current_provider = [], provider_idx
        self._update_providers()
        self._plans, self._current_plan = [], plan_idx
        self._update_plans()

    def _get_initials(self):
        client = GConf.Client.get_default()
        country_code = client.get_string(GCONF_SP_COUNTRY) or self.COUNTRY_CODE
        provider_name = client.get_string(GCONF_SP_PROVIDER) or ''
        plan_name = client.get_string(GCONF_SP_PLAN)

        country_el = self.root.find('.//country[@code="%s"]'% country_code)
        try:
            provider_idx, provider_el = [
                (idx, p_el)
                for idx, p_el in enumerate(country_el.findall('provider'))
                if p_el.find('name').text == provider_name
            ][0]
        except IndexError:
            provider_idx = 0
            plan_idx = 0
        else:
            plan_names = [self._get_localized_or_default_name(p_el)
                          for p_el in provider_el.findall('.//apn')]
            plan_idx = plan_names.index(plan_name)

        return country_code, provider_idx, plan_idx

    def _store_defaults(self):
        country_code = self.get_country().code
        provider_name = self.get_provider().name
        plan_name = self.get_plan().name
        print "Saving ", plan_name
        client = GConf.Client.get_default()
        client.set_string(GCONF_SP_COUNTRY, country_code)
        client.set_string(GCONF_SP_PROVIDER, provider_name)
        client.set_string(GCONF_SP_PLAN, plan_name)

    def set_country(self, idx):
        self._current_country = idx
        self._update_providers()
        self.set_provider(0)

    def set_provider(self, idx):
        self._current_provider = idx
        self._update_plans()
        self.set_plan(0)

    def set_plan(self, idx):
        self._current_plan = idx

    def _get_country_element(self):
        return self.root.find('country[%s]' % (self._current_country + 1))

    def _get_providers_elements(self):
        return [provider
                for provider in self._get_country_element().findall('provider')
                if provider.find('.//gsm')]

    def _get_provider_element(self):
        idx = self._current_provider
        # Warning! XPath index begins with 1
        return self._get_country_element().find('.//provider[%s]'
                                                % (int(idx) + 1))

    def _get_plan_elements(self):
        return self._get_provider_element().findall('.//apn')

    def _get_localized_or_default_name(self, el):
        tag = el.find('name[@%s="%s"]' % (self.LANG_NS_ATTR, self.LANG))
        if tag is None:
            tag = el.find('name')
        if tag is not None:
            name = tag.text
        else:
            name = _('Default')
        return name

    def get_countries(self):
        return self._countries

    def _update_providers(self):
        self._providers = []
        for idx, provider_el in enumerate(self._get_providers_elements()):
            name = self._get_localized_or_default_name(provider_el)
            provider = Provider(idx, name)
            self._providers.append(provider)
        return self._providers

    def get_providers(self):
        return self._providers

    def _update_plans(self):
        self._plans = []
        for idx, apn_el in enumerate(self._get_plan_elements()):
            name = self._get_localized_or_default_name(apn_el)
            username_tag = apn_el.find('username')
            password_tag = apn_el.find('password')
            plan = {
                'apn': apn_el.get('value'),
                'name': name,
                'username': username_tag.text if username_tag is not None else None,
                'password': password_tag.text if password_tag is not None else None,
            }
            self._plans.append(Plan(idx, **plan))
        return self._plans

    def get_plans(self):
        return self._plans

    def get_country(self):
        return self._countries[self._current_country]

    def get_provider(self):
        return self._providers[self._current_provider]

    def get_plan(self):
        return self._plans[self._current_plan]
