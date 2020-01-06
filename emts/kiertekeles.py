metrikafile = "metrikak/metrikak"
with open('%s' % metrikafile, 'r') as m:
    line = m.readline()
    while line:
        print("Line {}".format(line.strip()))
        sp = line.split(',')
        line = m.readline()