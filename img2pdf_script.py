# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 21:52:44 2019

@author: Owner
"""

import os
import img2pdf

files = os.listdir()
files = list(filter(lambda x: x.endswith('.jpg'), files))

for fi in files:
    pdf_fi = fi.split('.')[0] + '.pdf'
    with open(pdf_fi, 'wb') as f:
        f.write(img2pdf.convert(fi))
