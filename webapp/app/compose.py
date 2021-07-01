#!/usr/bin/env python
"""
Given a CSV containing some fields, generate letters of thanks
and announcments to those on whose behalf gifts were made.
"""

import os
import sys 
import re
import app.htmlier as htmlier
import datetime
import pandas as pd
from collections import Counter

donee_template = """Dear $DONEE$,
We are pleased to inform you that $TYPE$
$PARTICIPLE$ been made to the church
$HONOREE$
From
$DONOR$
We give thanks to God for these gifts.

$ADDRESS1$
$ADDRESS2$
$DATE$"""

donor_template = """Dear $DONOR$,
Thank you for your gift$PLURAL$
$$AMOUNT$
given to the church $HONOREE$
$ACK$$DONEE$
We give thanks to God for your gift.

$ADDRESS1$
$ADDRESS2$
$DISCLAIMER1$
$DISCLAIMER2$
$DATE$"""

ack = """An acknowledgement of your gift
has been sent to
"""
acks = """Acknowledgements of your gifts
have been sent to
"""


def donor_thanks(donor, fields, address, disclaimer):
    result = donor_template
    result = re.sub('\$DONOR\$',donor, result)
    multiple = False
    if len(fields['amounts']) > 1:
        multiple=True
        result = re.sub('\$AMOUNT\$', str(sum([int(float(x)) for x in fields['amounts']])), result)
    else:    
        result = re.sub('\$AMOUNT\$', fields['amounts'][0], result)
    tmp = ""    
    for hon in fields['honorees']:
        if hon:
            tmp+=hon+'\n'
    tmp = re.sub('of ', 'of\n', tmp)
    tmp = re.sub('In ', 'in ', tmp)
    result = re.sub('\$HONOREE\$', tmp, result)
    result = re.sub('\$ADDRESS1\$', address[0], result)
    result = re.sub('\$ADDRESS2\$', address[1], result)
    result = re.sub('\$DISCLAIMER1\$', disclaimer[0], result)
    result = re.sub('\$DISCLAIMER2\$', disclaimer[1], result)

    tmp = ""
    if fields['donees'] and fields['donees'][0]:
        if multiple:
            result = re.sub('\$ACK\$', acks, result)
        else:    
            result = re.sub('\$ACK\$', ack, result)
        for don in fields['donees']:
            if don:
                tmp+=don+'\n'
        result = re.sub('\$DONEE\$', tmp, result)
    else:
        result = re.sub('\$ACK\$', "", result)
        result = re.sub('\$DONEE\$', "", result)

    if multiple:
        result = re.sub('\$PLURAL\$', 's totaling', result)
    else:    
        result = re.sub('\$PLURAL\$', ' of', result)

    result = re.sub('\$DATE\$', datetime.date.today().strftime("%B %d, %Y"), result)
    return result

def donee_announce(donee, fields, address):
    result = donee_template
    result = re.sub('\$DONEE\$', donee, result)
    multiple_donors = len(fields['donors']) > 1
    counts = Counter(fields['types'])
    multiple_types = len(counts) > 1
    tmp=fields['honoree']
    tmp = re.sub('of ', 'of\n', tmp)
    tmp = re.sub('In ', 'in ', tmp)
    result = re.sub('\$HONOREE\$', tmp, result)
    result = re.sub('\$ADDRESS1\$', address[0], result)
    result = re.sub('\$ADDRESS2\$', address[1], result)
    tmp = ""
    for don in fields['donors']:
        if don:
            tmp+=don+'\n'
    result = re.sub('\$DONOR\$', tmp, result)
    if multiple_donors:
        result = re.sub('\$PARTICIPLE\$', 'have', result)
    else:
        result = re.sub('\$PARTICIPLE\$', 'has', result)
    tmp = ""
    if multiple_donors:
        tmp = "\n"
        for i, tp in enumerate(list(set(fields['types']))):
            if i:
                tmp+=' and '
            tmp+=tp+'s\n'
    else:
        tmp = "a\n"+fields['types'][0]
    result = re.sub('\$TYPE\$', tmp, result)

    result = re.sub('\$DATE\$', datetime.date.today().strftime("%B %d, %Y"), result)
    return result

def donor_totals(records):
    donor_dict = {}
    for rec in records:
        if rec['donor'] not in donor_dict:
            donor_dict[rec['donor']] = {'amounts':[], 'honorees':[], 'donees':[]}
        if rec['amount'] != '---':
            donor_dict[rec['donor']]['amounts'].append(rec['amount'])
        else:    
            donor_dict[rec['donor']]['amounts'].append('0')
        donor_dict[rec['donor']]['honorees'].append(rec['honoree'])
        donor_dict[rec['donor']]['donees'].append(rec['donee'])
    return donor_dict

def donee_totals(records):
    donee_dict = {}
    for rec in records:
        if rec['donee'] not in donee_dict:
            donee_dict[rec['donee']] = {'honoree':rec['honoree'], 'donors':[], 'types':[]}
        donee_dict[rec['donee']]['donors'].append(rec['donor'])
        donee_dict[rec['donee']]['types'].append(rec['type'])
    return donee_dict
        
def all_records(handle):
    temp_df = pd.read_excel(handle)
    handle.close()
    temp_csv_path = os.path.join("/var/tmp/", os.path.basename(handle.name))+".csv" 
    temp_df.to_csv(temp_csv_path, index=False)
    
    handle = open(temp_csv_path, 'r', encoding='utf-8')
    lines = handle.readlines()
    handle.close()
    result = []
    for line in lines[1:]:
        #line = line.decode("utf-8")
        values = re.split(',', line.strip())
        if values[0]:
            result.append( 
                dict(zip(
                    ['honoree', 'donor', 'amount', 'donee', 'type'], 
                    values)))
    return result


def generate_notes(handle, address_line_1, address_line_2, disclaimer_line_1, disclaimer_line_2):
    records = all_records(handle)
    don_tots = donor_totals(records)
    dee_tots = donee_totals(records)
    htm = htmlier.HTMLier()
    content = ""
    content += '<hr class="pb">'
    content += htm.tag("b", "Donors")
    for donor,data in don_tots.items():
        note = '<p style="page-break-before: always">'
        note += '<hr class="pb">'
        temp = donor_thanks(donor, data,
                            [address_line_1, address_line_2],
                            [disclaimer_line_1, disclaimer_line_2])
        lines = re.split('\n', temp)
        mid = ""
        reg = True
        for line in lines:
            if "No goods" in line:
                reg = False
            if not reg:
                mid += htm.tag('i', line, style='font-size: 9pt;')
            else:    
                mid += htm.tag('i', line)
            mid += "<br>"
        note += htm.tag('div', mid) 
        content += note 

    content += '<hr class="pb">'
    content += htm.tag("b", "Donees")
    for donee,data in dee_tots.items():
        note = '<p style="page-break-before: always">'
        note += '<hr class="pb">'
        temp = donee_announce(donee, data, [address_line_1, address_line_2])
        lines = re.split('\n', temp)
        mid = ""
        for line in lines[0:-1]:
            mid += htm.tag('i', line)
            mid += "<br>"

        mid += htm.tag('i', lines[-1], style='font-size: 9pt;')    
        mid += "<br>"
        note += htm.tag('div', mid) 
        content += note

    
  
    return content
