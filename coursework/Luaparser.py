#time to go to work
# keywords:
# and	break	do	else	elseif
# end	false	for	function	if
# in	local	nil	not	or
# repeat	return	then	true	until	while

#Can either do a backtracking parser or a predictive parser
#Predictive probably the best choice but requires look ahead

import re

#variable name list
varNames = []
#function name list
funcNames = []

#regular expressions used 
last = re.compile('return|break')
#a variable or function name must be alphanumeric but not containing only numbers and cannot be a keyword
varFuncName = '[0-9]*[a-zA-Z_](\w)*'
var = re.compile(varFuncName)
func = re.compile('function( )*'+varFuncName+'(('+varFuncName+',( )*)*'+varFuncName+')')

#counter for keeping track of loopDepth
loopDepth = 0
errorsFound = False


def checkErrors():
  global errorsFound
  if (not errorsFound):
    errorsFound = True
    print("Errors found")

def chunk(data, count):
  #a chunk can be broken on return or break
  #break can only be used when in a loop
  statementsExecuting = True
  while (statementsExecuting and count < len(data)):
    if last.match(data[count]):
      count = laststat(data, count) + 1
      statementsExecuting = False
    else:
      count = stat(data, count) + 1
  return count

def block(data, count):
  return chunk(data, count)

def stat(data, count):
  
  return count

def laststat(data, count): 
  if re.match('break', data[count]) and loopDepth > 0:
    #don't decrease loopDepth until we find an end
    return count
  else: #we are matching with 'return'
    if re.search(' ', data[count]):
      #if this occurs then we are dealing with a variable name most likely
      explist(data[count][6:].strip( ), count)
    return count

def explist(xList, count):
  #apparently it is fully possible to return several different types in a list!
  x = ""
  while (len(xList) > 0):
    #need to break up the string
    if (re.match('\'', xList)):
      #got to make sure when we find another ' that it isn't an escaped character
      charCount = 1
      x = xList[:charCount]
      searching = True
      while (searching):
        index = xList[charCount:].find('\'')
        if (index == -1):
          checkErrors()
          print("Expected \' to close string on line ", count+1)
          return
    exp(x, count)
  #{exp() ','} exp()

def exp(x, count):
  '''
  nil or
  false or
  true or
  Number() or
  String() or
  '...' or 
  function() or
  prefixexp() or
  tableconstructor() or
  exp() binop() exp() or
  unop() exp()


def stat():
  varlist() '=' explist() or
  functioncall() or
  do block() end or
  while exp() do block() end or
  repeat block() until exp() or
  if exp() then block() 
  {elseif exp() then block()} #potentially repeats
  [else block()] end or
  for Name() '=' exp ',' exp [',' exp] do block() end or
  for namelist() in explist() do block() end or
  function funcname() funcbody() or
  local function Name() funcbody() or
  local namelist() ['=' explist()]

def funcname():
  Name() {',' Name()} [':' Name()]

def varlist():
  var() {',' var()}

def var():
  Name() or
  prefixexp() '[' exp() ']' or
  prefixexp() '.' Name

def namelist():
  Name {',' Name}


def prefixexp():
  var() or
  functioncall() or
  '(' exp() ')'

def functioncall():
  prefixexp() args() or
  prefixexp() ':' Name() args()

def args():
  '(' [explist()] ')' or
  tableconstructor() or
  String()

def function():
  function funcbody()

def funcbody():
  '(' [parlist()] ')' block() end

def tableconstructor():
  '{' [fieldlist()] '}'

def fieldlist():
  field() {fieldsep() field()} [fieldsep]

def field():
  '[' exp() ']' '=' exp() or
  Name() '=' exp() or
  exp()

def fieldsep():
  ',' or
  ';'

def binop():
  '+' or '-' or '*' or '/' or '^' or '%' or '..' or
  '<' or '<=' or '>' or '>=' or '==' or '~=' or
  and or or

def unop():
  '-' or not or '#'
'''

def printFunctions(data):
    for x in data:
        if (func.search(x)):
            print(x)

def parse(filename):
  
  with open(filename) as f:
    data = f.readlines()
  
  #break each line by whitespace characters
  data = [x.split(';') for x in data]
  strippedData = []
  for y in data:
    for x in y:
      x = x.strip( )
      strippedData.extend([x])
  
  data = strippedData
  print(block(data, 0))
  print(data)
  #runs if no errors are detected
  global errorsFound
  if (not errorsFound): printFunctions(data)

if __name__ == "__main__":
  import sys
  try:
    parse(sys.argv[1])
  except IndexError:
    print("Need to provide a lua file to parse")