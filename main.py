# import requests
import logging
import sys
import csv

# constants
layerSeperator = "^"
partSeperator = "+"
propertySeperator = "~"
topOfBoard = 'top'
botOfBoard = 'bottom'
lcscUrl = 'https://jlcpcb.com/componentSearch/uploadComponentInfo'

# only absolute paths work here since it is called by the EAGLE ULP apparently... adjust for yourself

logFile = '/Users/tlubes/Documents/EAGLE/development/jlcsmt/file.log'
# partLib = '/Users/tlubes/Documents/EAGLE/development/jlcsmt/lcsc.xls'
pnpFile = '/Users/tlubes/Documents/EAGLE/development/jlcsmt/jlcsmt-pnp.csv'
bomFile = '/Users/tlubes/Documents/EAGLE/development/jlcsmt/jlcsmt-bom.csv'

# init logging

logging.basicConfig(filename=logFile,level=logging.DEBUG)

# fetch lcsc library

# libFile = requests.get(lcscUrl)
# open(partLib, 'wb').write(libFile.content)

# organize parts into dict

partDict = {}
partDict[topOfBoard] = []
partDict[botOfBoard] = []

topData = sys.argv[1].split(layerSeperator)[0]
bottomData = sys.argv[1].split(layerSeperator)[1]

logging.debug(sys.argv[1])


if topData:
    for part in topData.split(partSeperator):
        topPart = {}
        topPart['name'] = part.split(propertySeperator)[0]
        topPart['x'] = part.split(propertySeperator)[1] + 'mm'
        topPart['y'] = part.split(propertySeperator)[2] + 'mm'
        topPart['angle'] = part.split(propertySeperator)[3].replace('_', '')
        topPart['value'] = part.split(propertySeperator)[4]
        topPart['package'] = part.split(propertySeperator)[5]
        topPart['library'] = part.split(propertySeperator)[6]
        topPart['device'] = part.split(propertySeperator)[7]
        partDict[topOfBoard].append(topPart)

if bottomData:
    for part in bottomData.split(partSeperator):
        bottomPart = {}
        bottomPart['name'] = part.split(propertySeperator)[0]
        bottomPart['x'] = part.split(propertySeperator)[1] + 'mm'
        bottomPart['y'] = part.split(propertySeperator)[2] + 'mm'
        bottomPart['angle'] = part.split(propertySeperator)[3].replace('_', '')
        bottomPart['value'] = part.split(propertySeperator)[4]
        bottomPart['package'] = part.split(propertySeperator)[5]
        bottomPart['library'] = part.split(propertySeperator)[6]
        bottomPart['device'] = part.split(propertySeperator)[7]
        partDict[botOfBoard].append(bottomPart)
     
# prepare bom file list

bomList = []

if topData:
    for part in partDict[topOfBoard]:
        foundPart = False
        for mat in bomList:
            if mat["library"] == part["library"] and mat["device"] == part["device"] and mat["comment"] == part["value"]:
                logging.debug('here')
                mat['designator'] += ("," + part['name'])
                foundPart = True
                break
        if foundPart is False:
            bomList.append({'designator': part['name'], 'comment': part['value'], 'footprint': part['package'], 'library': part['library'], 'device': part['device']})

if bottomData:
    for part in partDict[botOfBoard]:
        foundPart = False
        for mat in bomList:
            if mat["library"] == part["library"] and mat["device"] == part["device"] and mat["comment"] == part["value"]:
                mat['designator'] += ("," + part['name'])
                foundPart = True
                break
        if foundPart is False:
            bomList.append({'designator': part['name'], 'comment': part['value'], 'footprint': part['package'], 'library': part['library'], 'device': part['device']})        

# writing pnp file

with open(pnpFile, mode='w') as file:
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # this is the header row of the csv table
    writer.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
    if topData:    
        for part in partDict[topOfBoard]:
            writer.writerow([part['name'],part['x'], part['y'], 'Top', part['angle']])

    if bottomData:  
        for part in partDict[botOfBoard]:
            writer.writerow([part['name'],part['x'], part['y'], 'Bottom', part['angle']])         

# writing bom file

with open(bomFile, mode='w') as file:
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # this is the header row of the csv table
    writer.writerow(['Comment', 'Designator', 'Footprint', 'LCSC Part'])    
    for part in bomList:
        writer.writerow([part['comment'], part['designator'], part['footprint'], ""])
