#!/usr/bin/python

from lxml import etree
from copy import deepcopy

#input tree
tree = etree.parse('dummy.xml')

#output tree
body = etree.Element('body')
output = etree.ElementTree(body)

key_parts = ["gramGrp/pos", "usg"]

for e in tree.xpath(".//entry[form/@type='lemma']"):
    # extract lemma base form
    lemma = e.find("form[@type='lemma']").text
    # look up lemma base entry in output tree
    query = './/entry' + ''.join(["[{}]".format(key+"='{}'".format(e.xpath(key)[0].text)) for key in key_parts] )
    query += "[form/@type='lemma'][form='{}']".format(lemma)
    # run query on output lemma entry list
    output_entry = output.xpath(query)
    # if lemma has no entry element in output yet, create one by copying current element from wordlist
    if len(output_entry) < 1:
        output_entry = deepcopy(e)
        output.getroot().append(output_entry)
    else:
        # if lemma is already in output list, add specific flexions from current wordlist element
        output_entry = output_entry[0]
        for a in e.findall("form[@type='non_lemma']"):
            output_entry.append(a)

output.write('out.xml')
        


