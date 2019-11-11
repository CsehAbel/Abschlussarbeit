import subprocess
import re

task = subprocess.Popen("cat szoveg.txt | docker run -i mtaril/emtsv tok,spell,morph,pos,conv-morph,dep,chunk,ner", shell=True, stdout=subprocess.PIPE)

with open('emChunker.txt', 'w') as f:
    for item in task.stdout.readlines():
        f.write("%s\n" % item.decode('utf-8'))
#Dokumentálni a feldarabolást vizuálisan
with open('emChunker.txt') as f:
    sor = f.readline()
    while sor:
        patternStem = re.compile('^(.*?)\s.*"stem": \["([1-9a-zA-ZÁÉÍÓÖŐÚÜŰaéíóöőúüű]+?)".*\s([^\s]+?)\s[^\s]+$')
        resultStem = patternStem.match(sor)

        patternLemma = re.compile('^(.*?)\s.*"lemma": "([1-9a-zA-ZÁÉÍÓÖŐÚÜŰaéíóöőúüű]+?)".*\s([^\s]+?)\s[^\s]+$')
        resultLemma = patternLemma.match(sor)

        patternRaw = re.compile('^([1-9a-zA-ZÁÉÍÓÖŐÚÜŰaéíóöőúüű\-]+?)\s.*\s([^\s]+?)\s[^\s]+$')
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

#1. B-NP E-NP      B-NP I-NP,I-NP...E-NP  külön array ba    --> második dokumentum  1. ugyanez
#2. a vektorokból kiszűrjük a központozást                                          2. ugyanaz
#3. bag of words = egy set-et csinálunk az összes szóból
#4. megcsináljuk az 1. lépésből a vektorokat                                        3. a létező bag of words ot felhasználva vektorokat csinálunk

#a vektorizált NP-nek vesszük a cosinus hasonlóságát az összes többivel a másodikból, a legnagyobb értéket eltároljuk
#az értékeket összeadjuk minden egyes NP-re az első dokumentomból, ez a szám megmutatja mennyire hasonló a második doksival
arrayNPext = []
with open('emChunker.txt') as f:
    sor = f.readline()
    arrayNPint = []
    while sor:
        patternStem = re.compile('^(.*?)\s.*"stem": \["([a-zA-ZÁÉÍÓÖŐÚÜŰaéíóöőúüű]+?)".*\s([^\s]+?)\s[^\s]+$')
        resultStem = patternStem.match(sor)
        patternLemma = re.compile('^(.*?)\s.*"lemma": "([a-zA-ZÁÉÍÓÖŐÚÜŰaéíóöőúüű]+?)".*\s([^\s]+?)\s[^\s]+$')
        resultLemma = patternLemma.match(sor)
        patternRaw = re.compile('^([a-zA-ZÁÉÍÓÖŐÚÜŰaéíóöőúüű\-]+?)\s.*\s([^\s]+?)\s[^\s]+$')
        resultRaw = patternRaw.match(sor)
        patternPunct = re.compile('^(.*?)\s.*\s([^\s]+?)\s[^\s]+$')
        resultPunct = patternPunct.match(sor)
        NP = ""
        sorArray = []
        if resultStem:
            sorArray.extend([resultStem.group(2), resultStem.group(3)])
            NP = resultStem.group(3)
        elif resultLemma:
            sorArray.extend([resultLemma.group(2), resultLemma.group(3)])
            NP = resultLemma.group(3)
        elif resultRaw:
            sorArray.extend(resultRaw.groups())
            NP = resultRaw.group(2)
        elif resultPunct:
            sorArray.extend(resultPunct.groups())
        else:
            pass

        if NP == "B-NP":
            arrayNPint.append(sorArray)
        elif NP == "I-NP" or NP == "E-NP":
            i = len(arrayNPint)-1
            while i >= 0:
                if arrayNPint[i][1] == "I-NP":
                    i = i-1
                    continue
                elif arrayNPint[i][1] == "B-NP":
                    arrayNPint.append(sorArray)
                    arrayNPext.append(arrayNPint)
                    arrayNPint = []
                    break
                else:
                    break




        sor = f.readline()

#assert task.wait() == 0
'''task2 = subprocess.Popen("cat emChunker.txt | sed -r 's#^.*\"stem\": \[\"([a-zA-ZÁÉÍÓÖŐÚÜŰaéíóöőúüű]+?).*$#\\1#'", shell=True, stdout=subprocess.PIPE)
for item in task2.stdout.readlines():
    print(item.decode('utf-8'))

'''
# If you need to use the regex more than once it is suggested to compile it.
'''
pattern = re.compile("\n")
result = pattern.sub('',raw)
pattern2 = re.compile("(\w+\s){3,}\w")
result2 = pattern2.finditer(result)
print(result)
'''

'''Nézzük meg, hogy chunker két enyhén eltérő szövegrészletre ugyanott darabolja-e szét a szövegeket'''
'''for sor in data:
    words = []
    if re.match('^.*"stem": \["([a-zA-ZÁÉÍÓÖŐÚÜŰaéíóöőúüű]+?)".*$', sor):
        print('lel')
        words.append(re.sub(r'^.*"stem": \["([a-zA-ZÁÉÍÓÖŐÚÜŰaéíóöőúüű]+?)".*$', r"\1", sor))
'''
#result = re.sub(r"(\d.*?)\s(\d.*?)", r"\1 \2", string1)
#^.*"stem": \["([a-zA-ZÁÉÍÓÖŐÚÜŰaéíóöőúüű]+?)".*$
#sorted(list(set(words)))

