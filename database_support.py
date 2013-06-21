import os
from xml.etree.cElementTree import ElementTree
import logging

COUNTRY_CODES_PATH = '/usr/share/zoneinfo/iso3166.tab'
PROVIDERS_FORMAT_SUPPORTED = '2.0'
PROVIDERS_PATH = '/usr/share/mobile-broadband-provider-info/serviceproviders.xml'

def has_providers_db():
    if not os.path.isfile(COUNTRY_CODES_PATH):
        logging.debug("Mobile broadband provider database: Country " \
                          "codes path %s not found.", COUNTRY_CODES_PATH)
        return False
    try:
        tree = ElementTree(file=PROVIDERS_PATH)
    except (IOError, SyntaxError), e:
        logging.debug("Mobile broadband provider database: Could not read " \
                          "provider information %s error=%s", PROVIDERS_PATH)
        return False
    else:
        elem = tree.getroot()
        if elem is None or elem.get('format') != PROVIDERS_FORMAT_SUPPORTED:
            logging.debug("Mobile broadband provider database: Could not " \
                          "read provider information. %s is wrong format.",
                          elem.get('format'))
            return False
        return True


def main():
    print "Has provider?", has_providers_db()


if __name__ == '__main__':
    main()
