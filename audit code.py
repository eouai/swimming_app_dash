
# coding: utf-8

# In[3]:



import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict
import csv
import codecs
#import cerberus
import schema
import os


# In[6]:


OSMFILE = "map.osm"
#OSMFILE = SAMPLE_FILE
validate_zip = re.compile(r'^[0-9]{5}(?:-[0-9]{4})?$')
#street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


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
zip_mapping = { 'UT84028': '84028',
           'UT84310': '84310',
           'UT84339': '84339',
           'Utah84328': '84328',
           '84306-9729': '84306'           
            }


def audit_zipcode(zip_types, zipcode):
    m = validate_zip.search(zipcode)
    if m:
        zip_type = m.group()
        #print(street_type)
        if zip_type not in expected_zip:
            #street_type = update_name(street_type, mapping)
            #print(street_type)
            zip_types[zip_type].add(zipcode)


def is_zip(elem):
    return (elem.attrib['k'] == "addr:postcode")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    zip_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "tag":
            tag_k = elem.attrib['k']
            if tag_k in ['addr:postcode']:
                tag_v = elem.attrib['v'].replace(' ','')
                
            for tag in elem.iter("tag"):
                if is_zip(tag):
                    audit_zipcode(zip_types, tag.attrib['v'])
    osm_file.close()
    return zip_types


def update_zip(name, mapping):
    
    # YOUR CODE HERE
    m = validate_zip.search(name)
    zipcode_raw = m.group()
    if zipcode_raw in mapping.keys():
        zipcode_updated = mapping[zipcode_raw]
        name = re.sub(zipcode_raw, zipcode_updated, name)
    #print(name)  
    return name


# In[9]:


zip_types = audit(OSMFILE)
pprint.pprint(dict(zip_types))
for zip_type, ways in zip_types.iteritems():
        for name in ways:
            better_zipcode = update_zip(name, zip_mapping)
            print(name, "=>", better_zipcode)

