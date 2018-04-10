#!/usr/bin/python

from lxml import etree
from copy import deepcopy

#input tree
tree = etree.parse('dummy.xml')

#output tree
body=etree.Element('body')
output=etree.ElementTree(body)

key_parts = ["[gramGrp/pos='{}']", "[usg='{}']"]

for e in tree.iter('entry'):
    lemma = e.find("form[@type='lemma']").text
    output_entry = output.find("entry[@lemma='{}']".format(lemma)) or etree.SubElement(body, 'entry', attrib={'lemma': lemma})
    print('lemma form {}, element in output tree: {}'.format(lemma, output_entry))
    for a in e.findall("form[@type='non_lemma']"):
        output_entry.append(a)

output.write('out.xml')
        


