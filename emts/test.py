import re

arrayNPext = []
with open('emChunker.txt') as f:
    sor = f.readline()
    arrayNPint = []
    while sor:
        patternStem = re.compile('^(.*?)\s.*"stem": \["([1-9a-zA-ZÁÉÍÓÖŐÚÜŰáéíóöőúüű]+?)".*\s([^\s]+?)\s[^\s]+$')
        resultStem = patternStem.match(sor)
        patternLemma = re.compile('^(.*?)\s.*"lemma": "([1-9a-zA-ZÁÉÍÓÖŐÚÜŰáéíóöőúüű]+?)".*\s([^\s]+?)\s[^\s]+$')
        resultLemma = patternLemma.match(sor)
        patternRaw = re.compile('^([1-9a-zA-ZÁÉÍÓÖŐÚÜŰáéíóöőúüű\-]+?)\s.*\s([^\s]+?)\s[^\s]+$')
        resultRaw = patternRaw.match(sor)
        patternPunct = re.compile('^(.*?)\s.*\s([^\s]+?)\s[^\s]+$')
        resultPunct = patternPunct.match(sor)
        NP = ""
        sorArray = []
        if resultStem:
            sorArray.extend([resultStem.group(2), resultStem.group(3)])
            NP = resultStem.group(3)
            print('%s, %s' % (resultStem.group(1), resultStem.group(3)))
        elif resultLemma:
            sorArray.extend([resultLemma.group(2), resultLemma.group(3)])
            NP = resultLemma.group(3)
            print('%s, %s' % (resultLemma.group(1), resultLemma.group(3)))
        elif resultRaw:
            sorArray.extend(resultRaw.groups())
            NP = resultRaw.group(2)
            print('%s, %s' % (resultRaw.group(1), resultRaw.group(2)))
        elif resultPunct:
            sorArray.extend(resultPunct.groups())
            NP = resultPunct.group(2)
            print('%s, %s' % (resultPunct.group(1), resultPunct.group(2)))
        else:
            sor = f.readline()
            continue

        if NP == "B-NP":
            if arrayNPint.__len__() > 0:
                arrayNPext.append(arrayNPint)
                arrayNPint = []
            arrayNPint.append(sorArray)
        elif NP == "I-NP" or NP == "E-NP":
            i = len(arrayNPint)-1
            while i >= 0:
                if arrayNPint[i][1] == "I-NP":
                    i = i-1
                    continue
                elif arrayNPint[i][1] == "B-NP":
                    arrayNPint.append(sorArray)
                    break
        sor = f.readline()

arrayNPextNonPunct = []
patternNonPunct = re.compile('[1-9a-zA-ZÁÉÍÓÖŐÚÜŰáéíóöőúüű\-]+')
for i in arrayNPext:
    arrayNPintNonPunct = []
    for j in i:
        if patternNonPunct.match(j[0]):
            arrayNPintNonPunct.append(j[0])
            print(j)
    print('\n')
    arrayNPextNonPunct.append(arrayNPintNonPunct)
