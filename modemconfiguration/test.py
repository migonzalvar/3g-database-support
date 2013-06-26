import unittest
from xml.etree.cElementTree import ElementTree

from .model import ServiceProvidersDatabase
from .config import PROVIDERS_PATH


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


if __name__ == '__main__':
    unittest.main()
