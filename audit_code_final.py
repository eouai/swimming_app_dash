#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 13:50:48 2018

@author: burtg-dev
"""

import csv
import codecs
#import pprint
import re
import xml.etree.cElementTree as ET
#import os
#import schema

#os.chdir('~/osm_audit/')

#import cerberus



OSM_PATH = "map.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
STREET_TYPE = re.compile(r'\b\S+\.?$', re.IGNORECASE)
VALIDATE_ZIP = re.compile(r'^[0-9]{5}$')

#SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

EXPECTED_STREET_TYPES = ['Street', 'Avenue', 'Boulevard', 'Drive', 'Court', 'Place',
                         'Square', 'Lane', 'Road', 'Trail', 'Parkway', 'Commons', 'East',
                         'West', 'North', 'South', 'Way', 'Paseo', 'Canyon', 'Main', 'Village']

EXPECTED_ZIP = [{'83287', '84028', '84302', '84303', '84306', '84307', '84309', '84310',
                  '84312', '84318', '84321', '84325', '84328', '84332', '84333', '84335',
                   '84337', '84339', '84340', '84341'}]

STREET_MAPPING = {'St': 'Street', 'St.': 'Street', 'Ave': 'Avenue', 'Rd.': 'Road',
                  'S': 'South', 'Hwy': 'Highway', 'Dr.': 'Drive', 'Rd': 'Road', 'vlg': 'Village'}

ZIP_MAPPING = { 'UT84028': '84028', 'UT84310': '84310', 'UT84339': '84339', 'Utah84328': '84328',
               '84306-9729': '84306', 'Utah 84328': '84328', }


def audit_street_type(street_name):
    m = STREET_TYPE.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in EXPECTED_STREET_TYPES:
            updated_street_type = update_street_type(street_type)
            street_name = re.sub(street_type, updated_street_type, street_name)
    return street_name

def audit_zip(zip_name):
    m = VALIDATE_ZIP.search(zip_name)
    if not m:
        zip_name = zip_name.strip()
        zip_name = update_zip(zip_name)
    return zip_name
        
def update_zip(zip_name):
    if zip_name in ZIP_MAPPING.keys():
        zip_name = ZIP_MAPPING[zip_name]
    return zip_name
            
def update_street_type(street_type):
    if street_type in STREET_MAPPING.keys():
        street_type = STREET_MAPPING[street_type]
    return street_type

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    if element.tag == 'node':
        for item in node_attr_fields:
            node_attribs[item] = element.attrib[item]
        for tag in element.iter("tag"):
            tagd={}
            if PROBLEMCHARS.search(tag.attrib['k']):
                pass
            elif tag.get('k'):
                if LOWER_COLON.search(tag.attrib['k']):
                    tagd['id'] = element.attrib['id']
                    tagd['key'] = tag.attrib['k'].split(':',1)[1]
                    tagd['type'] = tag.attrib['k'].split(':',1)[0]
                    tagd['value'] = tag.attrib['v']
                else:
                    tagd['id'] = element.attrib['id']
                    tagd['key'] = tag.attrib['k']
                    tagd['value'] = tag.attrib['v']
                    tagd['type'] = 'regular'
                if tag.attrib['k'] == 'addr:street':
                    tagd['value'] = audit_street_type(tagd['value'])
                if tag.attrib['k'] == 'addr:postcode' or tag.attrib['k'] == 'postal_code':
                    tagd['value'] = audit_zip(tagd['value'])
                
                tags.append(tagd)

        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for item in way_attr_fields:
            way_attribs[item] = element.attrib[item]
        id_counter = 0
        for nd in element.iter('nd'):
            way_nodes_d = {}
            way_nodes_d['id'] = element.attrib['id']
            #print(way_nodes_d['id'])
            way_nodes_d['node_id'] = nd.attrib['ref']
            #print(way_nodes_d['node_id'])
            way_nodes_d['position'] = id_counter
            #print(way_nodes_d['position'])
            id_counter += 1
            way_nodes.append(way_nodes_d)
        for tag in element.iter("tag"):
            tagd={}
            if PROBLEMCHARS.search(tag.attrib['k']):
                pass
            elif tag.get('k'):
                if LOWER_COLON.search(tag.attrib['k']):
                    tagd['id'] = element.attrib['id']
                    tagd['key'] = tag.attrib['k'].split(':',1)[1]
                    tagd['type'] = tag.attrib['k'].split(':',1)[0]
                    tagd['value'] = tag.attrib['v']
                else:
                    tagd['id'] = element.attrib['id']
                    tagd['key'] = tag.attrib['k']
                    tagd['value'] = tag.attrib['v']
                    tagd['type'] = 'regular'
                if tag.attrib['k'] == 'addr:street':
                    tagd['value'] = audit_street_type(tagd['value'])
                if tag.attrib['k'] == 'addr:postcode' or tag.attrib['k'] == 'postal_code':
                    tagd['value'] = audit_zip(tagd['value'])
                    
                tags.append(tagd)

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


#def validate_element(element, validator, schema=SCHEMA):
#    """Raise ValidationError if element does not match schema"""
#    if validator.validate(element, schema) is not True:
#        field, errors = next(validator.errors.iteritems())
#        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
#        error_string = pprint.pformat(errors)
        
#        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        #validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
#                if validate is True:
#                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)
