import re
import os
import sys

pattern = re.compile("([\w\-]+\.sml):(\d+)\.(\d+)(-(\d+)\.(\d+))? Error: ")
exceptionType = "exception Err\n"

def getFirstErrMessage(message):
    return pattern.match(message)

cmfile = sys.argv[1]

foundError = True
count = 0
while foundError and (count < 1000):
    stream = os.popen("echo \"OS.Process.exit OS.Process.success;\" | sml -m " + cmfile + " 2> /dev/null")

    foundError = False
    for line in stream:
        matchOpt = getFirstErrMessage(line)
        if matchOpt != None:
            if "syntax error: " in line:
                print "We can't fix syntax errors! That's on you!"
                sys.exit(1)
            foundError = True
            print "Found a type error, fixing it!"
            filename = matchOpt.group(1)
            startRow = int(matchOpt.group(2)) - 1
            startCol = int(matchOpt.group(3)) - 2
            endRow = matchOpt.group(5)

            if endRow == None:
                endRow = startRow
            else:
                endRow = int(endRow) - 1

            endCol = matchOpt.group(6)
            if endCol == None:
                endCol = startCol + 1
            else:
                endCol = int(endCol)

            with open(filename, "r+") as f:
                content = f.readlines()
                for i in xrange(len(content)):
                    if i == startRow and i < endRow:
                        # keep up to start col
                        content[i] = content[i][0:(startCol)] + "raise Err\n"
                    elif i > startRow and i < endRow:
                        content[i] = ""
                    elif i > startRow and i == endRow:
                        # keep after end col
                        if (endCol < len(content[i])):
                            content[i] = content[i][(endCol):]
                        else:
                            content[i] = ""
                    elif i == startRow and i == endRow:
                        content[i] = (content[i][0:(startCol)]) + "raise Err" + (content[i][(endCol):])
                        if content[i] != '\n':
                            content[i] = content[i] + "\n"
                f.seek(0)
                if content[0] != exceptionType:
                    content = [exceptionType] + content
                if count < 1000:
                    f.write("".join(content))
                else:
                    f.write ("fun id x = x\n")
                f.truncate()
                count = count + 1

print "Your code no longer contains any type errors"
