import subprocess
import re
import numpy


def docker_to_file(in_file, out_file):
    task = subprocess.Popen("cat %s | docker run -i mtaril/emtsv tok,spell,morph,pos,conv-morph,dep,chunk,ner" % in_file, shell=True, stdout=subprocess.PIPE)
    with open('%s' % out_file, 'w') as f:
        for item in task.stdout.readlines():
            f.write("%s\n" % item.decode('utf-8'))

# arrayNPext[....................................................................................]
#             arrayNPint[.............................................]     arrayNPint[....]
#                            np['stem','B-NP']...np['stem','E-NP']
def generate_3d_array(out_file):
    #Dokumentálni a feldarabolást vizuálisan
    arrayNPext = []
    with open('%s' % out_file) as f:
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
    #1. B-NP E-NP      B-NP I-NP,I-NP...E-NP  külön array ba    --> második dokumentum  1. ugyanez
    #2. a vektorokból kiszűrjük a központozást                                          2. ugyanaz
    #3. bag of words = egy set-et csinálunk az összes szóból
    #4. megcsináljuk az 1. lépésből a vektorokat                                        3. a létező bag of words ot felhasználva vektorokat csinálunk

    #a vektorizált NP-nek vesszük a cosinus hasonlóságát az összes többivel a másodikból, a legnagyobb értéket eltároljuk
    #az értékeket összeadjuk minden egyes NP-re az első dokumentomból, ez a szám megmutatja mennyire hasonló a második doksival
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
    return arrayNPextNonPunct

#Bag_of_words
def generate_bow(ddd_array):
    words = []
    for a in ddd_array:
        words.extend([b for b in a])
    words = sorted(list(set(words)))
    return words

def generate_bow_matrix(bow,ddd_array):
    bag_vectors = numpy.zeros(len(bow))
    for np in ddd_array:
        bag_vector = numpy.zeros(len(bow))
        for npWord in np:
            for count, word in enumerate(bow):
                if word == npWord:
                    bag_vector[count] += 1
        bag_vectors = numpy.vstack((bag_vectors, bag_vector))
        print("{0}\n{1}\n".format(np, numpy.array(bag_vector)))
    return bag_vectors


#docker_to_file('szoveg.txt', 'emChunker.txt')
#docker_to_file('szoveg1.txt', 'emChunker1.txt')
#docker_to_file('szoveg2.txt', 'emChunker2.txt')

bow = generate_bow_matrix(generate_bow(generate_3d_array('emChunker.txt')), generate_3d_array('emChunker.txt'))
bow1 = generate_bow_matrix(generate_bow(generate_3d_array('emChunker.txt')), generate_3d_array('emChunker1.txt'))
bow2 = generate_bow_matrix(generate_bow(generate_3d_array('emChunker.txt')), generate_3d_array('emChunker2.txt'))

from numpy import dot
from numpy.linalg import norm


def compare_bows(bow_1, bow_2):
    sum_of_max = 0
    for vector_b1 in bow_1:
        max_cos_sim = 0
        for vector_b2 in bow_2:
            if numpy.count_nonzero(vector_b1) == 0 or numpy.count_nonzero(vector_b2) == 0:
                continue
            cos_sim = dot(vector_b1, vector_b2) / (norm(vector_b1) * norm(vector_b2))
            if max_cos_sim < cos_sim:
                max_cos_sim = cos_sim
        sum_of_max += max_cos_sim
    return sum_of_max

print(compare_bows(bow, bow1))
print(compare_bows(bow, bow2))


import urllib.request
import bs4
import html5lib


def get_text_bs(html):
    tree = bs4.BeautifulSoup(html, 'html5lib')

    body = tree.body
    if body is None:
        return None

    for tag in body.select('script'):
        tag.decompose()
    for tag in body.select('style'):
        tag.decompose()

    text = body.get_text(separator='\n')
    return text


tidy = lambda c: re.sub(
    r'(^\s*[\r\n]+|^\s*\Z)|(\s*\Z|\s*[\r\n]+)',
    lambda m: '\n' if m.lastindex == 2 else '',
    c)

#html = urllib.request.urlopen('https://totalcar.hu/magazin/hirek/')
#raw = get_text_bs(html)
#print(tidy(raw))




