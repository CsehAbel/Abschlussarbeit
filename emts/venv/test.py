import re

with open('your_file.txt') as f:
    sor = f.readline()
    while sor:
        patternStem = re.compile('^(.*?)\s.*"stem": \["([a-zA-ZÁÉÍÓÖŐÚÜŰaéíóöőúüű]+?)".*\s([^\s]+?)\s[^\s]+$')
        resultStem = patternStem.match(sor)

        patternLemma = re.compile('^(.*?)\s.*"lemma": "([a-zA-ZÁÉÍÓÖŐÚÜŰaéíóöőúüű]+?)".*\s([^\s]+?)\s[^\s]+$')
        resultLemma = patternLemma.match(sor)

        patternRaw = re.compile('^([a-zA-ZÁÉÍÓÖŐÚÜŰaéíóöőúüű\-]+?)\s.*\s([^\s]+?)\s[^\s]+$')
        resultRaw = patternRaw.match(sor)

        patternPunct = re.compile('^(.*?)\s.*\s([^\s]+?)\s[^\s]+$')
        resultPunct = patternPunct.match(sor)

        if resultStem:
            print("%s , %s, %s" % (resultStem.group(1), resultStem.group(2), resultStem.group(3)))
        elif resultLemma:
            print("%s , %s, %s" % (resultLemma.group(1), resultLemma.group(2), resultLemma.group(3)))
        elif resultRaw:
            print("%s , %s" % (resultRaw.group(1), resultRaw.group(2)))
        elif resultPunct:
            print("%s , %s" % (resultPunct.group(1), resultPunct.group(2)))
        else:
            print(sor)
        sor = f.readline()