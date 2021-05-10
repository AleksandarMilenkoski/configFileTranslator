from os import listdir, makedirs, sep
from os.path import isfile, dirname, realpath, exists
import time, re
from yandex import Translater


class InputErrorType(Exception):
    def __init__(self):
        super().__init__('Wrong input type. Input have to be of Match object type')


def toTranslateCheck(stringToCheck):
    # flagToTranslate = False
    stringToCheckLowerCases = stringToCheck.lower()
    rusEngSeparator = '|'
    russianLetters = ['б', 'в', 'г', 'д', 'ё', 'ж', 'з', 'и', 'й', 'л', 'п', 'ф', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ь', 'э',
                      'ю', 'я']
    englishLettersPrim = ['b', 'd', 'f', 'g', 'h', 'i', 'l', 'm', 'n', 'q', 'r', 's', 't', 'u', 'v', 'w', 'z']
    englishLettersSecond = ['a', 'c', 'e', 'j', 'k', 'o', 'p', 'x', 'y']
    if stringToCheckLowerCases.find(rusEngSeparator) != -1:
        separatorIndex = stringToCheckLowerCases.find(rusEngSeparator)
        for engLetter in englishLettersPrim:
            if stringToCheckLowerCases.find(engLetter, separatorIndex) != -1:
                return False
        for engLetter in englishLettersSecond:
            if stringToCheckLowerCases.find(engLetter, separatorIndex) != -1:
                return False
        # return False

    for letter in russianLetters:
        if stringToCheckLowerCases.find(letter) != -1:
            return True

    return False


def stringSeparate(stringToSeparate):
    # regex = '^([0-9]|\w|\.|\@|\-)*\@'
    # regex = '^(\d|\w|\W)*(\]|\^|\*|\@)\s*'
    regex = '^(\d|\w|\W)*(\]|\^|\*|\@|\=)\s*'  # only for lines.txt
    matchObject = re.search(regex, stringToSeparate)
    if matchObject == None:
        return None
    else:
        span = matchObject.span()
        # print(stringToSeparate[:span[1]])
        # print(stringToSeparate[span[1]:])
        return [stringToSeparate[:span[1]], stringToSeparate[span[1]:]]


def isSeparatable(stringToCheck, regexStr):
    matchObject = re.search(regexStr, stringToCheck)
    return matchObject


def separateString(matchObject, stringToSeparate):
    if matchObject.__class__.__name__ != 'SRE_Match':
        raise InputErrorType

    span = matchObject.span()

    return [stringToSeparate[:span[1]], stringToSeparate[span[1]:]]


currentDirectoryName = dirname(realpath(__file__))
listOfFilesForTranslation = listdir(currentDirectoryName)

translater = Translater.Translater()
translater.set_key('trnsl.1.1.20190421T162143Z.c04c67a8b5b0f466.f18d54390a1f41d21e7b0dd6ebb5706e585670fb')
translater.set_from_lang('ru')
translater.set_to_lang('en')

logDirName = '.' + sep + 'log' + sep
translatedFilesDirName = '.' + sep + 'translated' + sep
ciclusSleepTime = 0.05
flieExtension = 'txt'

if not exists(logDirName):
    makedirs(logDirName)

if not exists(translatedFilesDirName):
    makedirs(translatedFilesDirName)

for fileToTraslate in listOfFilesForTranslation:
    if fileToTraslate[-3:] == flieExtension:

        print(fileToTraslate[:-4])

        currentTranslatedFileName = fileToTraslate[:-4]

        if currentTranslatedFileName == 'lines':
            regexString = '^(\d|\w|\W)*(\]|\^|\*|\@|\=)\s*'
        else:
            regexString = '^(\d|\w|\W)*(\]|\^|\*|\@)\s*'

        lineNumber = 1
        numOfTranslatedCharacters = 0
        logFileName = logDirName + currentTranslatedFileName
        fileNameFrom = currentTranslatedFileName + '.txt'
        # fileNameTo = translatedFilesDirName + 'T' + currentTranslatedFileName + '.txt'
        fileNameTo = translatedFilesDirName + currentTranslatedFileName + '.txt'

        fileToWriteTo = open(fileNameTo, 'w')

        logFileNotTranslated = open((logFileName + 'NotTranslatedLog.txt'), 'w')
        logFileTranslated = open((logFileName + 'TranslatedLog.txt'), 'w')
        logFileStringSlices = open((logFileName + 'StringSlicesLog.txt'), 'w')

        with open(fileNameFrom) as lines:
            # print(lines)
            for line in lines:
                strippedLine = line.strip()

                print(lineNumber)

                if toTranslateCheck(line):
                    print('Translated')
                    print(strippedLine)
                    logFileTranslated.write(str(lineNumber) + '\n')
                    logFileTranslated.write(strippedLine + '\n')

                    tmpTranslated = ''
                    matchObject = isSeparatable(line, regexString)

                    if matchObject == None:
                        if line != '':
                            numOfTranslatedCharacters += len(line)
                            translater.set_text(line)
                            tmpTranslated = translater.translate()
                        fileToWriteTo.write(tmpTranslated)

                        logFileTranslated.write(tmpTranslated.strip() + '\n' + '\n')
                        print(tmpTranslated.strip())
                    else:
                        stringParts = separateString(matchObject, line)
                        if stringParts[1] != '':
                            numOfTranslatedCharacters += len(stringParts[1])
                            translater.set_text(stringParts[1])
                            tmpTranslated = translater.translate()
                        fileToWriteTo.write(stringParts[0] + tmpTranslated)

                        logFileStringSlices.write(str(lineNumber) + '\n')
                        logFileStringSlices.write(stringParts[0] + '\n')
                        logFileStringSlices.write(stringParts[1] + '\n' + '\n')

                        tempLogString = ''
                        tempLogString = stringParts[0] + tmpTranslated
                        logFileTranslated.write(tempLogString.strip() + '\n' + '\n')
                        print(tempLogString.strip())
                else:

                    fileToWriteTo.write(line)

                    logFileNotTranslated.write(str(lineNumber) + '\n')
                    logFileNotTranslated.write(strippedLine + '\n')
                    logFileNotTranslated.write(strippedLine + '\n' + '\n')

                    print('Not Translated')
                    print(strippedLine)
                    print(strippedLine)

                lineNumber += 1
                time.sleep(ciclusSleepTime)

        print('Number of translated characters ' + str(numOfTranslatedCharacters))
        logFileTranslated.write('Number of translated characters ' + str(numOfTranslatedCharacters) + '\n')

        fileToWriteTo.close()
        logFileNotTranslated.close()
        logFileTranslated.close()
        logFileStringSlices.close()


