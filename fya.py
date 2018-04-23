#!/usr/bin/python

import re

from lxml import etree
from copy import deepcopy

#input tree
tree = etree.parse('new_xpath_test_2.xml')

#output tree
body = etree.Element('body')
output = etree.ElementTree(body)

key_parts = ["gramGrp/pos"]

components = {
            "form": ["orth", "usg"],
            "sense": ["cit/quote"]
            }

def att_val_query(value):
    try:
        components = re.findall("([^']+|')", value)
    except Exception as e:
        print(e)
        print("unknown object: ", value)
        return "''"
    if len(components) > 1:
        return "concat({})".format(', '.join(["\"{}\"".format(c) for c in components]))
    else:
        return "\"" + components[0] + "\""



for entry in tree.xpath(".//entry[form/@type='lemma']"):
    # extract lemma base form
    lemma = entry.find("form[@type='lemma']").find("orth").text
    # look up lemma base entry in output tree
    query = './/entry' + ''.join(["[{}]".format(key+"='{}'".format(entry.xpath(key)[0].text)) for key in key_parts] )
    query += "[form/@type='lemma'][form/orth='{}']".format(lemma)
    # run query on output lemma entry list
    output_entry = output.xpath(query)
    # if lemma has no entry element in output yet, create one by copying current element from wordlist
    if len(output_entry) < 1:
        output_entry = deepcopy(entry)
        output.getroot().append(output_entry)
    else:
        # if lemma is already in output list, add specific flexions and shit like that from current wordlist element
        output_entry = output_entry[0]
        for elemname, criteria in components.items():
            for e in entry.xpath(elemname):
                query = ''.join(["[{}]".format(key+"="+att_val_query(e.xpath(key)[0].text)) for key in criteria if any([x != None for x in e.xpath(key)])] )
                try:
                    if len(output_entry.xpath(elemname + query)) < 1:
                        output_entry.append(e)
                except:
                    print(elemname + query)


output.write('out.xml', encoding="utf-8", pretty_print=True)
        


