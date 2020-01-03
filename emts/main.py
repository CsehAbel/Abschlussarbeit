import subprocess
import re
import numpy

#
def docker_to_file(in_file, out_file):
    task = subprocess.Popen("cat %s | docker run -i mtaril/emtsv tok,spell,morph,pos,conv-morph,dep,chunk,ner" % in_file, shell=True, stdout=subprocess.PIPE)
    with open('%s' % out_file, 'w') as f:
        for item in task.stdout.readlines():
            f.write("%s\n" % item.decode('utf-8'))

# arrayNPext[....................................................................................]
#             arrayNPint[.............................................]     arrayNPint[....]
#                            np['stem','B-NP']...np['stem','E-NP']
def generate_3d_array(out_file):
    arrayNPext = [] #Belső listái tartalmazzak a főnévi csoportokat
    with open('%s' % out_file) as f:
        sor = f.readline()
        arrayNPint = [] #Egy darab főnévi csoportot tartalmaz
        while sor: #A dokumentum e-magyar eszközlánc általi outputján soronként iterálunk végig
            patternStem = re.compile('^(.*?)\s.*"stem": \["([1-9a-zA-ZÁÉÍÓÖŐÚÜŰáéíóöőúüű]+?)".*\s([^\s]+?)\s[^\s]+$')
            resultStem = patternStem.match(sor) #a reguláris kifejezés egyezőségét tartlamazű boolean
            patternLemma = re.compile('^(.*?)\s.*"lemma": "([1-9a-zA-ZÁÉÍÓÖŐÚÜŰáéíóöőúüű]+?)".*\s([^\s]+?)\s[^\s]+$')
            resultLemma = patternLemma.match(sor)
            patternRaw = re.compile('^([1-9a-zA-ZÁÉÍÓÖŐÚÜŰáéíóöőúüű\-]+?)\s.*\s([^\s]+?)\s[^\s]+$')
            resultRaw = patternRaw.match(sor)
            patternPunct = re.compile('^(.*?)\s.*\s([^\s]+?)\s[^\s]+$')
            resultPunct = patternPunct.match(sor)
            NP = ""
            sorArray = []
            if resultStem: #megvizsgáljuk, melyik reguláris kifejezés illik az adott sorra és a kívánt egyezőségi csoportot
                           # azaz a szótövet és a főnévi csoportban elfoglalt helyet eltároljuk
                sorArray.extend([resultStem.group(2), resultStem.group(3)])
                NP = resultStem.group(3)
                #print('%s, %s' % (resultStem.group(1), resultStem.group(3)))
            elif resultLemma:
                sorArray.extend([resultLemma.group(2), resultLemma.group(3)])
                NP = resultLemma.group(3)
                #print('%s, %s' % (resultLemma.group(1), resultLemma.group(3)))
            elif resultRaw:
                sorArray.extend(resultRaw.groups())
                NP = resultRaw.group(2)
                #print('%s, %s' % (resultRaw.group(1), resultRaw.group(2)))
            elif resultPunct:
                sorArray.extend(resultPunct.groups())
                NP = resultPunct.group(2)
                #print('%s, %s' % (resultPunct.group(1), resultPunct.group(2)))
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
                #print(j)
        #print('\n')
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
        #print("{0}\n{1}\n".format(np, numpy.array(bag_vector)))
    return bag_vectors


#docker_to_file('szoveg.txt', 'emChunker.txt')
#docker_to_file('szoveg1.txt', 'emChunker1.txt')
#docker_to_file('szoveg2.txt', 'emChunker2.txt')

bow = generate_bow_matrix(generate_bow(generate_3d_array('emChunker.txt')), generate_3d_array('emChunker.txt'))
bow1 = generate_bow_matrix(generate_bow(generate_3d_array('emChunker.txt')), generate_3d_array('emChunker1.txt'))
bow2 = generate_bow_matrix(generate_bow(generate_3d_array('emChunker.txt')), generate_3d_array('emChunker2.txt'))

from numpy import dot
from numpy.linalg import norm

#compare bag_of_words
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

#Teszt
print(compare_bows(bow, bow1))
print(compare_bows(bow, bow2))


# Jaccard hasonlóság
def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))


def union(lst1, lst2):
    return list(set(lst1) | set(lst2))


def generate__array(out_file):
    with open('%s' % out_file) as f:
        sor = f.readline()
        arrayStem = []
        while sor: #A dokumentum e-magyar eszközlánc általi outputján soronként iterálunk végig
            patternStem = re.compile('^(.*?)\s.*"stem": \["([1-9a-zA-ZÁÉÍÓÖŐÚÜŰáéíóöőúüű]+?)".*\s([^\s]+?)\s[^\s]+$')
            resultStem = patternStem.match(sor) #a reguláris kifejezés egyezőségét tartlamazű boolean
            patternLemma = re.compile('^(.*?)\s.*"lemma": "([1-9a-zA-ZÁÉÍÓÖŐÚÜŰáéíóöőúüű]+?)".*\s([^\s]+?)\s[^\s]+$')
            resultLemma = patternLemma.match(sor)
            patternRaw = re.compile('^([1-9a-zA-ZÁÉÍÓÖŐÚÜŰáéíóöőúüű\-]+?)\s.*\s([^\s]+?)\s[^\s]+$')
            resultRaw = patternRaw.match(sor)
            if resultStem:
                arrayStem.extend(resultStem.group(2))
            elif resultLemma:
                arrayStem.extend(resultLemma.group(2))
            elif resultRaw:
                arrayStem.extend(resultRaw.group(1))
            else:
                sor = f.readline()
                continue
            sor = f.readline()
    return arrayStem


def jaccard_sim(out_file1, out_file2):
    i = intersection(generate__array(out_file1), generate__array(out_file2)).__len__()
    u = union(generate__array(out_file1), generate__array(out_file2)).__len__()
    return i/u


print(jaccard_sim('emChunker.txt', 'emChunker1.txt'))
print(jaccard_sim('emChunker1.txt', 'emChunker2.txt'))

#Euklideszi távolság
from scipy.spatial import distance

def compare_bows_eucl(bow_1, bow_2):
    sum_of_min = 0
    for vector_b1 in bow_1:
        min_eucl_sim = 99999999
        for vector_b2 in bow_2:
            if numpy.count_nonzero(vector_b1) == 0 or numpy.count_nonzero(vector_b2) == 0:
                continue
            eucl_sim = distance.euclidean(vector_b1, vector_b2)
            if min_eucl_sim > eucl_sim:
                min_eucl_sim = eucl_sim
        if min_eucl_sim != 99999999:
            sum_of_min += min_eucl_sim
    return sum_of_min

print(compare_bows_eucl(bow, bow1))
print(compare_bows_eucl(bow, bow2))

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

import codecs
f=codecs.open("cucc/1", 'r')
#html = urllib.request.urlopen('https://totalcar.hu/magazin/hirek/')
#raw = get_text_bs(html)
raw = get_text_bs(f)
#print(tidy(raw))

import os
directory_in_strcucc = "cucc"
directorycucc = os.fsencode(directory_in_strcucc)
directory_in_strout = "output"
directoryout = os.fsencode(directory_in_strout)

redo = []#[5295,5286,5336,3522,5307,5309,2502,5308,3712,5344,5317,4939,5292,3517,5549,5339,5335,2365,5332,5323,2722,2546,2545,5349,5557,5296,3758,3677,5348,2354,5315,2527,5331,5338,5009,5329,5347,351,3829,2361,3681,5326,5346,5322,5320,5293,5285,5300,5297,2195,5321,5305,3664,3686,5310,3711,5535,2921,5301,2406,2922,4039,5306,570,5289,5327,5334,598,5294,4396]

output_files = [os.fsdecode(h) for h in os.listdir(directoryout)]

for file in os.listdir(directorycucc):
    filename = os.fsdecode(file)
    #print("%s" % filename)
    if filename in redo:
        f = codecs.open("cucc/%s" % filename, 'r')
        raw = get_text_bs(f)
        out_file = "plaintext/%s" % filename
        with open('%s' % out_file, 'w') as g:
            g.write(raw)
        docker_to_file("plaintext/%s" % filename, "output/%s" % filename)
        print(filename)
    elif filename not in output_files:
        f = codecs.open("cucc/%s" % filename, 'r')
        raw = get_text_bs(f)
        out_file = "plaintext/%s" % filename
        with open('%s' % out_file, 'w') as g:
                g.write(raw)
        docker_to_file("plaintext/%s" % filename, "output/%s" % filename)

directory_in_strplaint = "plaintext"
directoryplaint = os.fsencode(directory_in_strplaint)
voltak = []
tulkicsik = [154,1744,2163,2169,2175,2180,2195,2207,2329,2338,2349,2354,2361,2365,2384,2398,2401,2406,2411,2414,2418,2424,2430,2452,2453,2454,2462,2469,2470,2471,2490,2500,2502,2527,253,2545,2546,2590,2591,2659,2661,2685,2693,2701,2707,2709,271,2711,2712,2713,2714,2715,2716,2717,2718,2719,272,2720,2721,2722,2734,2796,2813,282,2820,287,291,2921,2922,2923,2927,2955,2993,3000,3005,3011,3015,3016,3020,3035,3152,3316,3321,3323,3328,3334,3345,3346,3351,3377,3378,3447,3448,3450,3454,3455,3467,3470,3474,3478,3489,351,3511,3517,352,3522,3537,3538,3543,3565,3569,3643,3644,3647,3650,3656,3664,3677,3681,3686,3703,3711,3712,3726,3758,3766,3829,3939,3983,4010,4013,4022,4031,4033,4039,4077,4080,4083,4114,4143,4144,4145,4146,4147,4153,4163,4170,4171,4174,4176,4177,4178,4196,4203,4245,4276,4279,4387,4388,4396,4398,4403,4417,4422,4430,4435,4444,4445,4461,4464,4474,4475,4481,4491,4492,4566,4630,4636,4640,4646,4652,4658,4663,4668,4674,4679,4686,4695,4705,4711,4716,4727,473,4733,4738,474,4745,475,4751,4756,476,4761,4767,477,4773,4778,4779,478,4783,4788,479,4790,4796,480,4801,4802,4806,481,4812,4818,482,4823,4824,4828,483,484,4840,485,486,487,488,489,4899,490,4905,491,4910,4913,492,4929,493,4939,494,4941,495,496,497,498,499,5,500,5009,501,5014,502,503,504,505,506,507,508,509,5095,510,511,512,513,514,515,5152,5153,5154,5155,5156,5157,5158,5159,516,5160,5161,5162,5164,5165,5166,5167,517,5171,5173,5174,5175,5176,518,519,520,5201,521,522,5285,5286,5287,5288,5289,5290,5292,5293,5294,5295,5296,5297,5298,5300,5301,5304,5305,5306,5307,5308,5309,5310,5315,5316,5317,5319,5320,5321,5322,5323,5324,5326,5327,5328,5329,5330,5331,5332,5333,5334,5335,5336,5337,5338,5339,5340,5341,5343,5344,5345,5346,5347,5348,5349,5447,5448,5449,5450,5451,5452,5453,5454,5455,5456,5457,5459,5460,5461,5462,5463,5464,5465,5466,5467,5468,5469,5470,5471,5472,5474,5475,5476,5477,5478,5479,5480,5481,5482,5483,5487,5489,5490,5491,5492,5493,5494,5496,5497,5498,5499,5500,5501,5502,5503,5504,5507,5510,553,5535,5536,5537,5538,5539,554,5541,5549,5550,5557,556,5563,5564,557,5579,5580,5581,5582,5583,5584,5585,5586,5587,5588,5589,5590,5591,5592,5593,5594,5596,5597,5598,5599,5600,5601,5602,5603,5604,5605,5606,5607,5608,5609,5610,5612,5613,5614,5616,5618,5619,5620,5621,5624,5625,5627,5628,5629,5630,5631,5632,5634,5635,5636,5637,5638,5639,564,5640,5641,5642,5643,5645,5646,5647,5648,5649,565,568,5680,5681,5683,5684,5685,5686,5687,5688,5689,5690,5691,5692,5693,5694,5695,5696,5697,5698,5699,570,5700,5701,5703,5704,5705,5706,5707,5709,5710,5711,5712,5713,5714,5715,5716,5717,5718,5719,5720,5721,5722,5723,5724,5725,5726,5727,5728,5729,573,5730,5731,5732,5733,5734,5735,5736,5737,5738,5739,5740,5741,5743,5744,5745,5746,5747,5748,5749,575,5750,5751,5752,5753,5755,5756,5757,5758,5759,5760,5761,5762,5763,5765,5766,5768,5769,577,5770,5771,5772,5774,5775,5776,5777,5778,5779,5780,5781,5782,5783,5784,5785,5786,5787,5788,5789,5790,5791,5792,5793,5794,5795,5796,5797,5798,5799,5800,5801,5803,5804,5806,5807,5808,5809,5810,5811,5812,5813,5814,5815,5817,5818,5819,5820,5821,5822,5823,5824,5825,5826,5827,5828,5829,5830,5831,5832,5834,5835,5836,5837,5838,5839,5840,5841,5842,5843,5844,5845,5846,5847,5848,5849,5850,5851,5852,5853,5854,5855,5856,5857,5858,5859,5861,5863,5864,5865,5866,5867,5868,587,5870,5871,5872,5874,5875,5876,5877,5879,5880,5881,5882,5883,5884,5885,5886,5887,5888,5889,589,5890,5891,5892,5893,5895,5896,5897,5898,5899,5901,5902,5903,5904,5905,5906,5907,5908,5910,5911,5912,5913,5915,5916,5917,5918,5919,5920,5921,5923,5924,5925,5926,5927,5928,5929,5930,5931,5932,5933,5934,5935,5936,5937,5938,5939,5940,5941,5942,5944,5945,5946,5947,5948,5949,5950,5951,5952,5953,5954,5955,5956,5957,5958,5959,5960,5961,5962,5963,5964,5965,5966,5967,5968,5969,5970,5971,5972,5973,5974,5975,5976,5977,5978,598,5980,5981,5982,5983,5984,5985,5986,5987,5988,5989,5990,5991,5992,5993,5994,5995,5996,5998,5999,6000,6001,6002,6003,6004,6005,6006,6007,6008,6009,6010,6011,6012,6013,6014,6015,6016,6017,6018,6019,6020,6021,6022,6023,6024,6025,6026,6027,6028,6029,6031,6032,6033,6035,6037,6038,6039,6040,6041,6042,6043,6044,6045,6046,6047,6048,6049,6050,6051,6052,6054,6055,6057,6058,6059,6060,6061,6062,6063,6065,6066,6067,6068,6069,6070,6071,6072,6073,6075,6076,6077,6078,6079,6080,6081,6082,6083,6085,6086,6087,6088,6089,6090,6091,6092,6093,6095,6096,6097,6098,6099,6100,6101,6102,6103,6104,6105,6106,6107,6108,6109,6110,6111,6112,6114,6115,6116,6117,6118,6119,6120,6121,6122,6123,6124,6125,6126,6127,6128,6129,6130,6131,6132,6133,6134,6135,6136,6138,6139,6140,6141,6142,6144,6148,6149,6150,6151,6153,6154,6155,6156,6157,6158,6159,6160,6161,6162,6163,6164,6165,6166,6167,6168,6169,6170,6171,6172,6173,6174,6175,6176,6177,6178,6179,6180,6181,6182,6183,6184,6185,6186,6187,6188,6189]
#find ~/Pycharmm/emts/output/ -type f -size +0b -size -89b -exec ls -l {} + | sed  -r 's@^.*/([0-9]{1,4})$@\1@' | awk -vORS=, '{print $1}'
metrikafile = "metrikak/metrikak"
with open('%s' % metrikafile, 'w') as m:

    for file in os.listdir(directoryplaint):
        filename = os.fsdecode(file)
        f = codecs.open("plaintext/%s" % filename, 'r')

        if filename in tulkicsik:
            continue
        if generate__array(f.name).__len__() < 1:
            continue

        print(f.name)
        bow = generate_bow_matrix(generate_bow(generate_3d_array(f.name)), generate_3d_array(f.name))

        for bfile in os.listdir(directoryplaint):
            bfilename = os.fsdecode(bfile)
            bf = codecs.open("plaintext/%s" % bfilename, 'r')
            if bf.name not in voltak:
                bbow = generate_bow_matrix(generate_bow(generate_3d_array(f.name)), generate_3d_array(bf.name))
                '''print(f.name + ":" + bf.name)
                print(compare_bows(bow, bbow))
                print(jaccard_sim(f.name, bf.name))
                print(compare_bows_eucl(bow, bbow))
                '''
                m.write("%s,%s,%d,%d,%d" % (filename,bfilename,compare_bows(bow, bbow),jaccard_sim(f.name, bf.name),compare_bows_eucl(bow, bbow)))
                m.write("\r\n")
        voltak.append(f.name)
