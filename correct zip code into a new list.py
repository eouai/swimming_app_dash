
# coding: utf-8

# In[1]:



import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict
import csv
import codecs
#import cerberus
#import schema
import os


# In[2]:


OSMFILE = "map.osm"


# In[3]:


correct_postal_code_list = []
incorrect_postal_code_list = []

def validate_postal_code(code):
    validate_postal_code = re.compile(r'^[0-9]{5}(?:-[0-9]{4})?$')
                                        
    match = re.search(validate_postal_code,code)
    return match


def process_postal_codes(SAMPLE_FILE):
    for event,element in ET.iterparse(SAMPLE_FILE):
        if element.tag =='tag':
            tag_k = element.attrib['k']
            if tag_k in ['addr:postcode', 'postal_code']:
                tag_v = element.attrib['v'].replace(' ','')
                
                match = validate_postal_code(tag_v)
                if match:
                    correct_postal_code_list.append(tag_v)
                else:
                    incorrect_postal_code_list.append(tag_v)
                    
process_postal_codes(OSMFILE)

print(len(correct_postal_code_list))
print(sorted(correct_postal_code_list))


# In[4]:


set(correct_postal_code_list)


# In[5]:


print(len(incorrect_postal_code_list))
print(sorted(incorrect_postal_code_list))


# In[6]:


postal_codes_fixed = []
#des_wrong = incorrect_postal_code_list
for elements in incorrect_postal_code_list:
    fixed = re.sub('[^0-9]','', elements) 
    correct_postal_code_list.append(fixed)

print(len(correct_postal_code_list))    
print(sorted(correct_postal_code_list))

