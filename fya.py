#!/usr/bin/python

import re

from lxml import etree
from copy import deepcopy

from tqdm import tqdm

#input tree
tree = etree.parse('new_xpath_test_2.xml')

#output tree
body = etree.Element('body')
output = etree.ElementTree(body)

# xpath expressions addressing entry subelement to be used for lemma entry identification
key_parts = ["gramGrp/pos"]

# define entry subelements to be copied into output lemma list
# alongside their child nodes to be used for identification
components = {
            "form": ["orth", "usg"],
            "sense": ["cit/quote"]
            }

def att_val_query(key, value):
    """ generate xpath expression with condition @key="value"."""
    try:
        # if single quotes occur in value string, we need to break it up in
        # single pieces and reassemble it using xpath function concat
        value_parts = re.findall("([^']+|')", value)
    except Exception as e:
        # if we fail to split up value into one or more substrings,
        # that's a problem because value is apparently no string
        print(e)
        print("unknown object: ", value, "for key ", key)
        return "key=''"
    # according to number of single quotes in original value string,
    # conditionally use xpath function `concat` so that single quotes
    # don't break syntax
    if len(value_parts) > 1:
        return "concat({})".format(', '.join(["\"{}\"".format(c) for c in value_parts]))
    else:
        return key+"=\"" + value_parts[0] + "\""


# retrieve all entries with form/@type "lemma" in intput list
entries = tree.xpath(".//entry[form/@type='lemma']")
# init progress bar
pbar = tqdm(total=len(entries))

# iterate through all input list entries
for i, entry in enumerate(entries):
    # extract lemma base form
    lemma = entry.find("form[@type='lemma']").find("orth").text
    # look up lemma base entry in output tree
    # generate xpath query matching entries in output list that match the current
    # input list entry
    query = './/entry' + ''.join(
        ["[{}]".format(
            key+"='{}'".format(entry.xpath(key)[0].text))
        for key in key_parts] )
    query += "[form/@type='lemma'][form/orth='{}']".format(lemma)
    # run query on output lemma entry list
    output_entry = output.xpath(query)
    # if lemma has no entry element in output yet, create one by copying current element from wordlist
    if len(output_entry) < 1:
        output_entry = deepcopy(entry)
        output.getroot().append(output_entry)
    else:
        # if lemma is already in output list, go through predefined list of attributes
        # to look up elements in the current wordlist entry that should be copied
        # into output list lemma entry
        #
        # select output list entry
        output_entry = output_entry[0]
        # iterate through predefined subnode selectors
        for elemname, criteria in components.items():
            # query all input list entry subnode instances for this selector
            for e in entry.xpath(elemname):
                # make query for identifying a corresponding subelement in the output lemma list
                query = ''.join(
                    ["[{}]".format(
                        att_val_query(key, e.xpath(key)[0].text))
                    for key in criteria if any([x != None for x in e.xpath(key)])] )
                try:
                    # if corresponding subelement does not exist in the output list entry
                    # corresponding to the current entry, copy the subelement at hand to the
                    # output list entry
                    if len(output_entry.xpath(elemname + query)) < 1:
                        output_entry.append(e)
                except:
                    print(elemname + query)
    # update progress bar
    pbar.update(1)


output.write('out.xml', encoding="utf-8", pretty_print=True)
