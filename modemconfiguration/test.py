import unittest
from xml.etree.cElementTree import ElementTree

from mock import patch

from .model import ServiceProvidersDatabase
from .config import PROVIDERS_PATH
from .config import (GCONF_SP_COUNTRY,
                     GCONF_SP_PROVIDER,
                     GCONF_SP_PLAN)


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.tree = ElementTree(file=PROVIDERS_PATH)
        self.countries_xml = self.tree.findall('country')

    def find_country_idx(self, country_code):
        country_xml = self.tree.find('country[@code="%s"]' % country_code)
        return self.countries_xml.index(country_xml)

    def test_country_list(self):
        db = ServiceProvidersDatabase()
        country_list = db.get_countries()
        self.assertEqual(len(country_list), len(self.countries_xml))

    def test_provider_list(self):
        country_code = 'es'
        country = self.find_country_idx(country_code)
        providers_xml = self.tree.find('country[@code="%s"]' % country_code)
        providers_xml = providers_xml.findall('provider')
        db = ServiceProvidersDatabase()
        db.set_country(country)
        providers_list = db.get_providers()
        self.assertEqual(len(providers_list), len(providers_xml))

    def test_provider_details(self):
        country_code = 'es'
        country = self.find_country_idx(country_code)
        provider = 1
        provider_xml = self.tree.find('country[@code="%s"]' % country_code)
        provider_xml = provider_xml.find('provider[%s]' % (provider + 1))
        db = ServiceProvidersDatabase()
        db.set_country(country)
        db.set_provider(provider)
        provider = db.get_provider()
        self.assertTrue(provider.name, provider_xml.find('name').text)

    def test_plan_list(self):
        country_code = 'es'
        country = self.find_country_idx(country_code)
        provider = 1
        plans_xml = self.tree.find('country[@code="%s"]' % country_code)
        plans_xml = plans_xml.find('provider[%s]' % (provider + 1))
        plans_xml = plans_xml.findall('.//apn')
        db = ServiceProvidersDatabase()
        db.set_country(country)
        db.set_provider(provider)
        plans_list = db.get_plans()
        self.assertEqual(len(plans_list), len(plans_xml))

    def test_plan_details(self):
        country_code = 'es'
        country = self.find_country_idx(country_code)
        provider = 1
        plan = 0
        plan_xml = self.tree.find('country[@code="%s"]' % country_code)
        plan_xml = plan_xml.find('provider[%s]' % (provider + 1))
        plan_xml = plan_xml.find('.//apn[%s]' % (plan + 1))
        apn = plan_xml.attrib['value']
        db = ServiceProvidersDatabase()
        db.set_country(country)
        db.set_provider(provider)
        db.set_plan(plan)
        plan = db.get_plan()
        self.assertTrue(apn, plan.apn)

    def test_go_through_all_options_from_xml(self):
        db = ServiceProvidersDatabase()
        for country_idx, country_el in enumerate(self.tree.findall('country')):
            country_code = country_el.attrib['code']
            db.set_country(country_idx)
            country = db.get_country()
            self.assertEqual(country_code, country.code)
            provider_els = [p_el for p_el in country_el.findall('provider')
                                 if p_el.find('.//gsm')]
            if provider_els == []:
                self.assertIsNone(db.get_provider())
            for provider_idx, provider_el in enumerate(provider_els):
                db.set_provider(provider_idx)
                provider = db.get_provider()
                self.assertEqual(provider_el.find('name').text,
                                 provider.name)
                plan_els = provider_el.findall('.//apn')
                if plan_els == []:
                    self.assertIsNone(db.get_plan())
                for plan_idx, plan_el in enumerate(plan_els):
                    apn = plan_el.attrib['value']
                    db.set_plan(plan_idx)
                    plan = db.get_plan()
                    if plan:
                        self.assertEqual(apn, plan.apn)

    def test_go_trough_all_combo_options(self):
        db = ServiceProvidersDatabase()
        countries = db.get_countries()
        for country in countries:
            db.set_country(country.idx)
            new_country = db.get_country()
            self.assertEqual(country, new_country)
            providers = db.get_providers()
            for provider in providers:
                db.set_provider(provider.idx)
                new_provider = db.get_provider()
                self.assertEqual(provider.name, new_provider.name)
                plans = db.get_plans()
                for plan in plans:
                    db.set_plan(plan.idx)
                    new_plan = db.get_plan()
                    self.assertEqual(plan.name, new_plan.name)


class FakeGConfClient(object):
    store = {
        GCONF_SP_COUNTRY: '',
        GCONF_SP_PROVIDER: '',
        GCONF_SP_PLAN: '',
    }

    def get_string(self, key):
        return self.store[key]

    def set_string(self, key, value):
        self.store[key] = value
        return


class PersistenceTest(unittest.TestCase):
    LOCALE = ('hi_IN', 'UTF-8')

    def setUp(self):
        gconf_patcher = patch('gi.repository.GConf.Client.get_default')
        gconf_mock = gconf_patcher.start()
        gconf_mock.return_value = FakeGConfClient()
        self.addCleanup(gconf_patcher.stop)

        locale_patcher = patch('locale.getdefaultlocale')
        locale_mock = locale_patcher.start()
        locale_mock.return_value = self.LOCALE
        self.addCleanup(locale_patcher.stop)

    def test_read(self):
        default_country_code = self.LOCALE[0][3:5].lower()
        db = ServiceProvidersDatabase()
        country = db.get_country()
        self.assertEqual(country.code, default_country_code)
        db.set_country(0)
        new_country = db.get_country()
        new_provider = db.get_provider()
        new_plan = db.get_plan()
        db.save()

        db2 = ServiceProvidersDatabase()
        country2 = db2.get_country()
        provider2 = db2.get_provider()
        plan2 = db2.get_plan()
        self.assertEqual(country2.code, new_country.code)
        self.assertEqual(provider2.name, new_provider.name)
        self.assertEqual(plan2.name, new_plan.name)



if __name__ == '__main__':
    unittest.main()
