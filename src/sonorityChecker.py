#-------------------------------------------------------------------------------
# Name:         westerparse.py
# Purpose:      An application for evaluating Westergaardian species counterpoint
#
# Authors:      Robert Snarrenberg, Tony Li
# Copyright:    (c) 2020 by Robert Snarrenberg
# License:      BSD, see license.txt
#-------------------------------------------------------------------------------

# takes a score (source) with two or more parts (lines)
# and examines the sonorities 
# for conformity with the preference rules of species counterpoint

# NB: vlq parts and score Parts are numbered top to bottom
# NB: vPair parts are numbered bottom to top


from music21 import *

if 'westerparse' in __name__:
    from .vlChecker import *
    from . import context
    from . import theoryAnalyzerWP
    from . import theoryResultWP
else:
    from vlChecker import *
    import context
    import theoryAnalyzerWP
    import theoryResultWP

# -----------------------------------------------------------------------------
# MODULE VARIABLES
# -----------------------------------------------------------------------------

sonorityReport = ''

sonorityErrors = []
# set preferences for sonorities
onBeatImperfectMin = 75 # percentage
onBeatUnisonMax = 5 # percentage
onBeatPerfectMax = 20 # percentage
tiedOverDissonanceMin = 50 # percentage
offbeatDissonanceMin = 50 # percentage
# downbeatHarmonyDensity = 



# implement interest rules 
    # look for narrow ambitus
    # look for monotony of various types
        # repeated pitches
            # consecutive (limit in outer voices)
        # lack of steps
        # lack of skips
        # lack of intervallic variety
        # etc.
        # repeated sonority: consecutive, nonconsecutive

# sonority features:
    # pcDensity: number of distinct pcs divided by number of pitches
    # pitchDensity: number of distinct pitches divided by number of notes


# implement preference rules for sonority
    # run only if the voice-leading passes evaluation??
    # need to be able to access measure number for each sonority/interval for reporting to user
    # perhaps modify theoryAnalyzer's getVerticalPairs or get from elements of vPair
        # add attributes to vPair 
            # .measure (integer) for time of onset??
            # .onDownbeat (true, false)
        # see fourthSpeciesForbiddenMotions for assembly of onbeat and offbeat vPairs
    # count non-terminal measures
# prefer imperfect on beat (first, second, third)
    # count non-terminal perfect and imperfect
    # prefer, say, 75% imperfect
# on-beat unisons, non-terminal (first, second, third, fourth?)
# fifths and octaves, on-beat
    # report if at least one note's rule is an S rule 
# adjacent register of lines
    # weight terminal intervals more than internal intervals
    # look for preponderance of simple intervals, not compound
    # report if too many intervals larger than 12th?
    # report if any intervals equal to or greater than 15th
# first species: series of imperfect consonances, with or without change of direction
# second species: dissonance off beat
    # count offbeat dissonances, prefer, say, percentage greater than 50%
# third species: dissonance off beat
    # count offbeat dissonances, prefer, say, percentage greater than 50%
    # count final off-beat dissonances, prefer, say, percentage greater than 50%
# fourth species
    # if tied over, prefer dissonance
    # say, at least 50%
# first species, three parts
    # count pitch-class content of each non-terminal sonority (1, 2, 3)
        # prefer most with 3
    # if pc count = 2
        # prefer octave(double octave) to unison
        # prefer imperfect to perfect
    # if all intervals above bass = perfect
        # report if sonority is non-terminal
    # test adjacency of upper parts, rarely more than octave
    # test adjacency of lower parts, rarely more than twelfth

#def firstSpeciesSonorities(score, analyzer, partNum1=None, partNum2=None):
#    pass

# -----------------------------------------------------------------------------
# MAIN SCRIPTS
# -----------------------------------------------------------------------------

def getAllSonorities(score):
    # create the theory analyzer object
    analyzer = theoryAnalyzerWP.Analyzer()
    analyzer.addAnalysisData(score)
    # make a list of voiceLeading.verticalities that have notes
    vertList = analyzer.getVerticalities(score, classFilterList=('Note'))#, 'Rest'))
        # the contents are accessible with the following method:
        # verticality.getObjectsByPart(classFilterList, partNums=None)
    return vertList   

def getSonorityList(vertList):
    '''Assemble an explicit figured-bass description for each sonority that has a bass note.'''
    # get list of voice pairings with the bass
    bassUpperPartPairs = getBassUpperPairs(score)
    
    sonorityList = []
    n = 0
    while n < len(vertList):
        vert = vertList[n]
        sonority = []
        for partPair in bassUpperPartPairs:
            bassPart = vert.getObjectsByPart(partPair[0])
            upperPart = vert.getObjectsByPart(partPair[1])
            # if parts are notes, get the interval
            if bassPart and upperPart:
                intv = interval.notesToGeneric(bassPart, upperPart).undirected
                if 1 < intv < 10:
                    sonority.append(intv)
                elif intv == 15:
                    sonority.append(8)
                else:
                    sonority.append(intv % 7)
            # if the upper part is not a note, use a hyphen
            elif bassPart and not upperPart:
                sonority.append('-')
            # if the bass is not a note, use x
            else:
                sonority.append('x')
            sonorityList.append(sonority)
        n += 1    
    return sonorityList

def getFullSonorities(vertList):
    '''Given a list of all the verticalities, 
    select only those that have a note in every part'''
    texture = len(vertList[-1].objects)
    vertList = [vert for vert in vertList if len(vert.objects) == texture]
    return vertList
    

def getOnbeatVertList(vertList):
    onbeatVertList = [vert for vert in vertList if vert.beat(leftAlign=False) == 1.0]
    return onbeatVertList
    
def getOffbeatVertList(vertList):
    offbeatVertList = [vert for vert in vertList if vert.beat(leftAlign=False) != 1.0]
    return offbeatVertList

def printSonorityList(sonorityList):
    '''
    For each sonority, the intervals above the bass are listed from lowest to highest.
    '''
    # get the number of parts in the texture
    texture = len(sonorityList[0])
    # start with the highest part
    t = texture - 1
    print('figured bass progression')
    while t > -1:
        fb = ''
        for son in sonorityList:
            s = son[t]
            if len(str(s)) == 1: 
                fb = fb + ' ' + str(s) + '  '
            else:
                fb = fb + str(s) + '  '
        print(fb)
        t -= 1

def getDensityList(vertList):
    densityList = []
    n = 0
    while n < len(vertList):
        vert = vertList[n].getObjectsByClass('Note')
        pitchDensisty = getPitchDensity(vert)
        pitchClassDensity = getPitchClassDensity(vert)
        densityList.append((pitchDensisty, pitchClassDensity))
        n += 1
    return(densityList)
   
def printDensityReport(densityList):
    l = len(densityList)
    pdensity = 0
    pcdensity = 0
    for d in densityList:
        pdensity = pdensity + d[0]
        pcdensity = pcdensity + d[1]
    pitchDensityRating = pdensity/l
    pitchClassDensityRating = pcdensity/l    
    print('p den rating', '{:.1%}'.format(pitchDensityRating))
    print('pc den rating', '{:.1%}'.format(pitchClassDensityRating))
        
def getPitchDensity(noteList):
    pitches = []
    for note in noteList:
        if note.nameWithOctave not in pitches:
            pitches.append(note.nameWithOctave)
    density = len(pitches)/len(noteList)
    return round(density, 2)
#    return len(pitches)
    
def getPitchClassDensity(noteList):
    pcs = []
    for note in noteList:
        if note.name not in pcs:
            pcs.append(note.name)
    density = len(pcs)/len(noteList)
    return round(density, 2)
#    return len(pcs)

def isOpen(noteList):
    # take a sonority list (ordered high to low) and determine whether it is open or closed
    outerIntv = interval.notesToGeneric(noteList[0], noteList[-1]).undirected
    if outerIntv % 7 in {3, 6}:
        return True
    else: return False

def getBassUpperPairs(score):
    bassPartNum = len(score.parts)-1
    upperPartNums = []
    n = len(score.parts) - 2
    while n > -1:
        upperPartNums.append(n)
        n -= 1
    bassUpperPartPairs = []
    for partNum in upperPartNums:
        bassUpperPartPairs.append((bassPartNum, partNum))
#    bassUpperPartPairs = bassUpperPartPairs.sort(key = lambda x: x[1])
    return sorted(bassUpperPartPairs)
        
def getAdjacentPartPairs(score):
    n = len(score.parts) - 1
    adjacentPairs = []
    while n > 0:
        adjacentPairs.append((n, n-1))
        n -= 1
    return adjacentPairs

def getAdjacencyRatings(score):
    vertList = getAllSonorities(score)
    adjPairs = getAdjacentPartPairs(score)
    adjacencyReport = ''
    for pair in adjPairs:
        # initialize counter for intervals an octave or smaller
        # initialize counter for all intervals
        pairReport = 'Adjacency rating for parts ' + str(pair[1]+1) + ' and ' + str(pair[0]+1) + ': '
        simpleCount = 0
        fullCount = 0 
        for vert in vertList:
            if vert.getObjectsByPart(pair[0], classFilterList='Note') and vert.getObjectsByPart(pair[1], classFilterList='Note'):
                n1 = vert.getObjectsByPart(pair[0], classFilterList='Note')
                n2 = vert.getObjectsByPart(pair[1], classFilterList='Note')
                if interval.Interval(n1, n2).name == interval.Interval(n1, n2).semiSimpleName:
                    simpleCount += 1
                fullCount += 1
        pairReport = pairReport + '{:.1%}'.format(simpleCount/fullCount)
        adjacencyReport = adjacencyReport + '\n' + pairReport
    return adjacencyReport

def getBassUpperPair(noteList):
    # accepts a noteList ordered high to low, bass at end of list
    bassPartNum = len(noteList)-1
    upperPartNums = []
    n = len(noteList) - 2
    while n > -1:
        upperPartNums.append(n)
        n -= 1
    bassUpperPartPair = []
    for partNum in upperPartNums:
        bassUpperPartPair.append((bassPartNum, partNum))
#    bassUpperPartPairs = bassUpperPartPairs.sort(key = lambda x: x[1])
    return sorted(bassUpperPartPair)

# this script not in use
def getSonorityClass(noteList):
    bassUpperPartPair = getBassUpperPair(noteList)
    sonority = []
    for partPair in bassUpperPartPair:
        bassPart = noteList[partPair[0]]
        upperPart = noteList[partPair[1]]
#            print(vert[partPair[0]], vert[partPair[1]])
#            print(interval.notesToGeneric(vert[partPair[0]], vert[partPair[1]]).undirected)
        intv = interval.notesToGeneric(bassPart, upperPart).undirected
        if 1 < intv < 10:
            sonority.append(intv)
        elif intv == 15:
            sonority.append(8)
        else:
            sonority.append(intv % 7)
    return sonority
    
def getOnbeatDyads(score, analyzer, partNum1, partNum2):
    onbeatDyads = []
    vPairList = analyzer.getVerticalPairs(score, partNum1, partNum2)
    for vPair in vPairList:
        if vPair != None:
            # use isOnbeat(note) from vlChecker
            if isOnbeat(vPair[0]) and isOnbeat(vPair[1]):
                onbeatDyads.append(vPair)
    return onbeatDyads
      
def getOnbeatIntervals(score, analyzer, partNum1, partNum2):
    onbeatDyads = getOnbeatDyads(score, analyzer, partNum1, partNum2)
    # return lists of measure numbers
    onbeatConsonances = []
    onbeatDissonances = []
    onbeatUnisons = []
    onbeatOctaves = []
    onbeatPerfect = []
    onbeatImperfect = []
    # or, create an object for every vPair and give it attributes: 
        # consonance=True, unison=True, perfect=True, dissonance=False, simple=True, onbeat=True
        # measure, interval, 
    for vPair in onbeatDyads:
        if isConsonanceAboveBass(vPair[0], vPair[1]):
            onbeatConsonances.append(vPair[0].measureNumber)
        if isVerticalDissonance(vPair[0], vPair[1]):
            onbeatDissonances.append(vPair[0].measureNumber)
        if isUnison(vPair[0], vPair[1]):
            onbeatUnisons.append(vPair[0].measureNumber)
        elif isOctave(vPair[0], vPair[1]):
            onbeatOctaves.append(vPair[0].measureNumber)
        if isPerfectVerticalConsonance(vPair[0], vPair[1]):
            onbeatPerfect.append(vPair[0].measureNumber)
        elif isImperfectVerticalConsonance(vPair[0], vPair[1]):
            onbeatImperfect.append(vPair[0].measureNumber)
    print('on-beat consonance count:', len(onbeatConsonances))
    print('on-beat dissonance count:', len(onbeatDissonances))
    print('on-beat unison count:', len(onbeatUnisons))
    print('on-beat octave count:', len(onbeatOctaves))
    print('on-beat perfect intervals count:', len(onbeatPerfect))
    print('on-beat imperfect intervals count:', len(onbeatImperfect))
            
def isOnbeatVerticality(verticality):
    '''Tests whether a verticality is initiated on the downbeat.'''
    # does not work!!!
    vnotes = verticality.getObjectsByClass('Note')
    isOnbeat = True
    print(vert.offset)
    for note in vnotes:
        print(note)
        if note.beat != 1.0:
            vOnbeat = False
            break
    return isOnbeat

# based on context.assignSpecies(part)
def assignSpeciesToParts(score):
    for part in score.parts:
        if not part.species:
            assignSpecies(part)
       
def getSonorityRating(score, beatPosition=None, sonorityType=None, outerVoicesOnly=True, includeTerminals=False):
    '''
    Report the percentage of a given sonority type in the list of full-voiced verticalities.
    Valid options:
        beatPosition: ['on', 'off', None]
        sonorityType: ['imperfect', 'perfect', 'dissonant', 'unison', 'octave', None]
        outerVoicesOnly: [True, False]
        includeTerminals: [True, False]
    '''
    vertList = getFullSonorities(getAllSonorities(score))
    
    if beatPosition == 'on':
        vl = getOnbeatVertList(vertList)
    elif beatPosition == 'off':
        vl = getOffbeatVertList(vertList)
    else:
        vl = vertList
        
    # trim list if terminals excluded 
    if includeTerminals == False:
        vl = vl[1:-1]
        
    # count the number of parts in the final verticality, as a reliable measure of the basic texture
    texture = len(vertList[-1].objects)
    
    # select part pairs based on outer voice parameter
    if outerVoicesOnly == False:
        partPairs = getBassUpperPairs(score)
    elif outerVoicesOnly == True:
        partPairs =[[texture-1,0]] # [bass, top]
    
    # now count all the relevant sonorities if the match the given type
    if sonorityType == None:
        print('cannot evaluate for all sonority types at once, so choose one and try again')
        return
    # initialize the counter and divisor
    sonorityCount = 0
    # set list length to nonzero number 
    totl = len(vl) * len(partPairs)
    if totl == 0:
        totl = 1
    # count the relevant sonorites    
    for pair in partPairs:
        bassPartNum = pair[0]
        topPartNum = pair[1]
        for vert in vl:
            bassPart = vert.getObjectsByPart(bassPartNum, classFilterList='Note')
            topPart = vert.getObjectsByPart(topPartNum, classFilterList='Note')
            if sonorityType == 'imperfect' and isImperfectVerticalConsonance(bassPart, topPart):
                sonorityCount += 1
            elif sonorityType == 'perfect' and isPerfectVerticalConsonance(bassPart, topPart):
                sonorityCount += 1
            elif sonorityType == 'dissonant' and isVerticalDissonance(bassPart, topPart):
                sonorityCount += 1
            elif sonorityType == 'unison' and isUnison(bassPart, topPart):
                sonorityCount += 1
            elif sonorityType == 'octave' and isOctave(bassPart, topPart):
                sonorityCount += 1
    return '{:.1%}'.format(sonorityCount/totl)

    
    
#     for vPair in vPairList:
#         if vPair != None:
#             if isUnison(vPair[0],vPair[1]):
#                 uCount += 1
#     if uCount > unisonLimit:
#         error='The number of unisons is '+ str(uCount) + ', which exceeds the limit of ' +\
#                 str(unisonLimit) + '.'
#         prefErrors.append(error)

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    # self_test code
#    pass
#    source='../tests/TestScoresXML/FirstSpecies01.musicxml'
#    source='../tests/TestScoresXML/FirstSpecies02.musicxml'
#    source='../tests/TestScoresXML/FirstSpecies03.musicxml'
#    source='../tests/TestScoresXML/FirstSpecies04.musicxml'
    source='../tests/TestScoresXML/FirstSpecies10.musicxml'
#    source='../tests/TestScoresXML/SecondSpecies10.musicxml'
#    source='../tests/TestScoresXML/SecondSpecies20.musicxml'
#    source='../tests/TestScoresXML/SecondSpecies21.musicxml'
#    source='../tests/TestScoresXML/SecondSpecies22.musicxml'
#    source='../tests/TestScoresXML/ThirdSpecies01.musicxml'
#    source='../tests/TestScoresXML/FourthSpecies01.musicxml'
#    source='../tests/TestScoresXML/FourthSpecies20.musicxml'
#    source='../tests/TestScoresXML/FourthSpecies21.musicxml'
#    source='../tests/TestScoresXML/FourthSpecies22.musicxml'


    score = converter.parse(source)
    
    vl = getAllSonorities(score)
    fl = getFullSonorities(vl)
    sl = getSonorityList(vl)
    
    onvl = getOnbeatVertList(fl)
    ofvl = getOffbeatVertList(vl)
    print(len(vl), len(onvl), len(ofvl))

#    dl = getDensityList(vl)
#    print('overall density') 
#    printDensityReport(dl)

#    print('onbeat density') 
#    ondl = getDensityList(onvl) 
#    printDensityReport(ondl)

#    assignSpeciesToParts(score)

    
    print(getAdjacencyRatings(score))
    
    sonorityTypes = ['perfect', 'imperfect', 'dissonant']
#    for st in sonorityTypes:
#        rating = getSonorityRating(score, beatPosition='on', sonorityType=st, outerVoicesOnly=True, includeTerminals=False)
#        print('rating for', st, 'sonorities on the beat, terminals excluded:', rating)    
#-------------------------------------------------------------------------------
# eof
