#Pick largest fitting outputs:
from org.ergoplatform.appkit import *
from org.ergoplatform.appkit.impl import *
def largestFittingOutputs(outputsToSpend, depositAmount):
    valueList = []
    indexList = []
    total = 0
    for i in outputsToSpend:
        valueList.append(i.getValue())
    while total < (depositAmount * Parameters.OneErg):
        total += max(valueList)
        indexList.append(valueList.index(max(valueList)))
        valueList.pop(valueList.index(max(valueList)))
    inputsLen = len(outputsToSpend)
    rejectList = []
    for i in range(inputsLen):
        if i not in indexList:
            rejectList.append(i)
    for i in reversed(rejectList):
        del outputsToSpend[i]
    return outputsToSpend

def pruneToIndex(index, outputsToSpend):
    while len(outputsToSpend) > index+1:
        del outputsToSpend[-1]
    return outputsToSpend
