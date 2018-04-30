# one way of iterating through the child elements
import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict

OSMFILE = "map.osm"
validate_zip = re.compile(r'^[0-9]{5}(?:-[0-9]{4})?$')
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

expected_zip = [{'83287',
                 '84028',
                 '84302',
                 '84303',
                 '84306',
                 '84307',
                 '84309',
                 '84310',
                 '84312',
                 '84318',
                 '84321',
                 '84325',
                 '84328',
                 '84332',
                 '84333',
                 '84335',
                 '84337',
                 '84339',
                 '84340',
                 '84341'}]


# UPDATE THIS VARIABLE
zip_mapping = {'UT84028': '84028',
               'UT84310': '84310',
               'UT84339': '84339',
               'Utah84328': '84328',
               '84306-9729': '84306'
               }


def update_zip(name, mapping):
    print(name)
    m = validate_zip.search(name)
    zipcode_raw = m.group()
    if zipcode_raw in mapping.keys():
        zipcode_updated = mapping[zipcode_raw]
        name = re.sub(zipcode_raw, zipcode_updated, name)
    # print(name)
    return name


node_tag = {}
# def audit(OSMFILE):
osm_file = open(OSMFILE, "r")
zip_types = defaultdict(set)
for event, element in ET.iterparse(osm_file, events=("start",)):
    for child in element:

        # 'tag' elements
        if child.tag == 'tag':

            # parse 'tag' elements
            if PROBLEMCHARS.match(child.attrib["k"]):
                continue

            # relevant section for 'addr:street' attributes:
            elif LOWER_COLON.match(child.attrib["k"]):
                node_tag["type"] = child.attrib["k"].split(":", 1)[0]
                node_tag["key"] = child.attrib["k"].split(":", 1)[1]
                node_tag["id"] = element.attrib["id"]

                # use cleaning function:
                if child.attrib["k"] == 'addr:postcode':
                    node_tag["value"] = update_zip(child.attrib["v"], zip_mapping)
                # otherwise:
                else:
                    node_tag["value"] = child.attrib["v"]
