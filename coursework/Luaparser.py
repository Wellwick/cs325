#time to go to work
# keywords:
# and	break	do	else	elseif
# end	false	for	function	if
# in	local	nil	not	or
# repeat	return	then	true	until	while

#Can either do a backtracking parser or a predictive parser
#Predictive probably the best choice but requires look ahead

import re
import shlex

#variable names can replace function names in the normal execution process, it's weird
#could create copies of the variable/function name arrays at the beginning of chunks that can be overridden

#variables to keep track of location of data
data = []
count = 0

#variable name list is NOT necessary, uninitiated variables are given the nil value and catching TypeErrors is outside of scope
#function name list
funcNames = [[["factorial"], "n"], [["add1"], "x"], [["pasta"]], [["new", "riley", ":milo"], "pi", "cheese", "bread"]]

#regular expressions used 
last = re.compile('return|break')
#a variable or function name must be alphanumeric but not containing only numbers and cannot be a keyword
varFuncName = '[0-9]*[a-zA-Z_](\w)*'
Name = re.compile(varFuncName)
Number = re.compile('([0-9]+(\.[0-9]*)?)|(\.[0-9]+)')
String = re.compile('(\".*\")|(\'.*\')')
Binop = re.compile('(\+)|(\-)|(\*)|(\/)|(\^)|(\%)|(\.\.)|(\<)|(\<\=)|(\>)|(\>\=)|(\=\=)|(\~\=)|(and)|(or)')
Unop = re.compile('(\-)|(not)|(\#)')
Ellipse = re.compile('\.\.\.')
LongString = re.compile('\[(=)*\[')

#counter for keeping track of loopDepth
loopDepth = 0
errorsFound = False

#pops the next token, making it to the right line point
def error(string):
  global errorsFound
  global count
  if (not errorsFound):
    errorsFound = True
    print("Errors found")
   
  #error is passed in as a string with the line number
  newCount = count + 1 #increase by one since originally accessing array
  print("Error on line ",newCount,": " + string)


def getNextToken():
  global data
  global count
  token = data[count].get_token()
  while token == None or token == '':
    count = count + 1
    if count > len(data):
      #this means we have reached the end of the file
      count = count - 1
      return False
    token = data[count].get_token()
  
  return token

#pops and then replaces the next token, retains same line position
def viewNextToken():
  global data
  global count
  newCount = count
  token = data[newCount].get_token()
  while token == None or token == '':
    newCount = newCount + 1
    if newCount > len(data):
      #this means we have reached the end of the file
      return False
    token = data[newCount].get_token()
  
  data[newCount].push_token(token)
  return token

def chunk():
  #a chunk can be broken on return or break
  #break can only be used when in a loop
  statementsExecuting = True
  token = True
  while (token != False):
    token = getNextToken()
    print(token)
    if last.match(token):
      laststat(token)
    elif re.match('end', token):
      return token
    elif not re.match(';', token):
      # ';' can be skipped, so treating it as an empty statement
      stat(token)
      
  return False

def block():
  return chunk()

def stat(token):
  if re.match('function', token):
    #function funcname() funcbody()
    functionName = funcname()
    count = funcbody(functionName)

def laststat(token): 
  print("LastStat: " + token)
  if re.match('break', token) and loopDepth == 0:
    #don't decrease loopDepth until we find an end
    if loopDepth == 0:
      error("break encoutered not in a loop")
  else: #we are matching with 'return'
    try:
      nextToken = getNextToken()
      #if this occurs then we are dealing with a variable name most likely
      explist(nextToken)
    except ValueError:
      #likely occurs because an opened string was not closed
      #Specification says only expect strings on a single line
      error("Expected string to close")
      

def explist(token):
  #apparently it is fully possible to return several different types in a list!
  checkingExpressions = True
  expectingExpression = False
  while (checkingExpressions):
    #need to break up the string
    if token == False or not exp(token):
      #reached end of expression list
      if expectingExpression:
        error("Expected expression after ,")
      return
    
    #after the checking is finished, clean for next round of exp() removal
    lastToken = token
    token = viewNextToken()
    if(re.match(',', token)):
      getNextToken()
      token = getNextToken()
      expectingExpression = True
    else:
      return
  
  #{exp() ','} exp()

def funcname():
  # can just be a sequence of names
  token = getNextToken()
  if not Name.match(token):
    error("Expected function name")
    return [False]
  else:
    return [token]
  #Name() {',' Name()} [':' Name()]

def funcbody(funcName):
  newList = []
  if funcName[0] != False: #can occur if this a new expression
    newList.extend(funcName)
  token = getNextToken()
  #expection parenthesis
  if token != '(':
    error("Expecting parenthesis for function")
    return False
  
  token = getNextToken()
  if token == None or token == '':
    error("Expecting parenthesis closing for function", count)
    return False
  elif token != ')':
    #got a parlist()
    var = parlist(token, newList)
    
  #once this point is reached then the parameters have been entered
  token = block()
  if token != False and re.match('end', token):
    return True
  #'(' [parlist()] ')' block() end

def parlist(token, newList):
  if not Ellipse.match(token):
    namelist()
    token = viewNextToken()
    if token == ',':
      #we expect the next symbol to be an ellipse
      getNextToken()
      token = getNextToken()
      if not Ellipse.match(token):
        error("Expecting ellipse at final value")

def namelist():
  return
  
def exp(token):
  nextToken = viewNextToken()
  
  if nextToken != False and Binop.match(nextToken):
    step = exp(token)
    getNextToken() #pulling binop back out again
    return (step and exp(getNextToken()))
  if token == "nil" or token == "false" or token == "true" or String.match(token) or Number.match(token) or token == "'...'":
    return True
  elif Unop.match(token):
    val = exp(getNextToken())
    if val:
      return True
    else:
      error("Expected expression after " + token, count)
      return False
  elif re.match(token, "function"):
    #running function funcbody()
    val = funcbody([False])
    return val
  else:
    return False
      
  '''
  nil or                    DONE
  false or                  DONE
  true or                   DONE
  Number() or               DONE
  String() or               DONE
  '...' or                  DONE
  function() or             DONE?
  prefixexp() or
  tableconstructor() or
  exp() binop() exp() or
  unop() exp()              DONE
  


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

def function():         <In Progress>
  function funcbody()

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
'''

def printFunctions(data):
  for x in funcNames:
    string = "Function: " + x[0][0]
    for y in x[0][1:]:
      if re.match(":", y):
        string = string + " : " + y[1:]
      else:
        string = string + ", " + y
    if len(x) > 1:
      string = string + ", Parameters: " + x[1]
    for y in x[2:]:
      string = string + ", " + y
    print(string)

def parseLongStrings(data):
  #method to take long strings and convert into (possibly multiple) normal strings
  global count
  count = 0
  checked = False
  while (count < len(data)):
    if LongString.search(data[count]) and not checked:
      #should step through, making sure this is not part of a string
      checked = True
      thisLine = data[count]
      index = 0
      outerCatch = False
      inString = False
      while index < len(data[count]):
        line = data[count]
        if inString != False:
          while line[index] == '\\' and index < len(line):
            index = index + 2
          
          if index < len(line):
            if line[index] == inString:
              inString = False
        elif line[index] == "'" or line[index] == '"':
          inString = line[index]
        elif LongString.match(line[index:]):
          outerCatch = '\]'
          startIndex = index
          index = index + 1
          
          while line[index] == '=':
            outerCatch = outerCatch + '='
            index = index + 1
          
          outerCatch = outerCatch + '\]'
          outerExpr = re.compile(outerCatch)
          index = index + 1
          #need to save string up until this point
          thisLine = line[:startIndex] + '"'
          
          while index < len(line):
            if line[index] == '"':
              thisLine = thisLine + "\\\""
            elif outerExpr.match(line[index:]):
              thisLine = thisLine + '"'
              index = index + len(outerCatch) - 2
              thisLine = thisLine + line[index:]
              outerCatch = False
              break
            else:
              thisLine = thisLine + line[index]
            index = index + 1
          
          if outerCatch != False:
            error("Expected " + outerCatch + " by the end of the line")
          else:
            #need to save the data
            data[count] = thisLine
            checked = False
            print(thisLine)
            break
          #no change to count so that it checks through another time in case there are other 
          #long strings
            
        index = index + 1
    else:
      count = count + 1
  
  return data

def parse(filename):
  global data
  global count
  
  with open(filename) as f:
    data = f.readlines()
  
  data = parseLongStrings(data)
  count = 0
  strippedData = []
  for y in data:
      y = shlex.shlex(y, posix=True)
      strippedData.extend([y])
  
  data = strippedData
  
  print(block())
  
  #runs if no errors are detected
  global errorsFound
  if (not errorsFound): printFunctions(data)

if __name__ == "__main__":
  import sys
  try:
    parse(sys.argv[1])
  except IndexError:
    print("Need to provide a lua file to parse")