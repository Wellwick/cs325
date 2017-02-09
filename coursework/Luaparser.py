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


#variable name list
varNames = []
#function name list
funcNames = [["factorial", "n"], ["add1", "x"], ["pasta"], ["new", "pi", "cheese", "bread"]]

#regular expressions used 
last = re.compile('return|break')
#a variable or function name must be alphanumeric but not containing only numbers and cannot be a keyword
varFuncName = '[0-9]*[a-zA-Z_](\w)*'
Name = re.compile(varFuncName)
Number = re.compile('([0-9]+(\.[0-9]*)?)|(\.[0-9]+)')
String = re.compile('(\".*\")|(\'.*\')')
Binop = re.compile('(\+)|(\-)|(\*)|(\/)|(\^)|(\%)|(\.\.)|(\<)|(\<\=)|(\>)|(\>\=)|(\=\=)|(\~\=)|(and)|(or)')
Unop = re.compile('(\-)|(not)|(\#)')
func = re.compile('function( )*'+varFuncName+'(('+varFuncName+',( )*)*'+varFuncName+')')

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

def chunk(data, count):
  #a chunk can be broken on return or break
  #break can only be used when in a loop
  statementsExecuting = True
  while (statementsExecuting and count < len(data)):
    token = data[count].get_token()
    print(token)
    if last.match(token):
      count = laststat(token, data, count) + 1
      statementsExecuting = False
    else:
      count = stat(token, data, count)
      token = data[count].get_token()
      #if we encounter a ; have to carry on parsing on the same line
      if token != ';':
        #time to do another statement on the same line
        count = count + 1
      
        
  return count

def block():
  return chunk()

def stat(token):
  if re.match('function', token):
    #function funcname() funcbody()
    functionName = funcname()
    count = funcbody(functionName)
  return count

def laststat(token): 
  print("LastStat: " + token)
  try:
    nextToken = getNextToken()
  except ValueError:
    #likely occurs because an opened string was not closed
    #Specification says only expect strings on a single line
    error("Expected string to close")
  if re.match('break', token) and loopDepth == 0:
    #don't decrease loopDepth until we find an end
    if loopDepth == 0:
      error("break encoutered not in a loop")
  else: #we are matching with 'return'
    if nextToken != None and nextToken != '':
      #if this occurs then we are dealing with a variable name most likely
      return explist(nextToken, data, count)
  
  return count

def explist(token, data, count):
  #apparently it is fully possible to return several different types in a list!
  x = ""
  while (token != None and token != ''):
    #need to break up the string
    if not exp(token, data, count):
      #error message is return exp specific
      return count
    
    #after the checking is finished, clean for next round of exp() removal
    lastToken = token
    token = data[count].get_token()
    if(re.match(',', token)):
      token = data[count].get_token()
    elif token == None or token == '':
      return count
    else:
      err = "Expected , after " + lastToken
      error(err, count)
      return count
  
  #in the case that the while loop ends instead of returning then
  #have reached nothing when expecting another token
  error("Expected another value after final ,", count)
  return count
  #{exp() ','} exp()

def funcname(data, count):
  # can just be a sequence of names
  token = data[count].get_token()
  if not Name.match(token):
    checkErrors()
    error("", count)
    
  return token
  #Name() {',' Name()} [':' Name()]

def funcbody(funcName, data, count):
  newList = []
  if funcName[0] != '': #can occur if this a new expression
    newList.extend(funcName)
  token = data[count].get_token()
  #expection parenthesis
  if token != '(':
    error("Expecting parenthesis for function", count)
    return [count, False]
  
  token = data[count].get_token()
  if token == None or token == '':
    error("Expecting parenthesis closing for function", count)
    return [count, False]
  elif token != ')':
    #got a parlist()
    count = parlist(token, newList, data, count)
    
  #once this point is reached then the parameters have been entered
  
  return count
  #'(' [parlist()] ')' block() end

def exp(token, data, count):
  nextToken = viewToken(
  while (nextToken == None or nextToken == ''):
    count = count + 1
    if (count > len(data):
      count 
      break
    nextToken = data[count].get_token()
  
  data[count].push_token(nextToken)
  
  if nextToken != None and nextToken != '' and Binop.match(nextToken):
    step = exp(token, [], count)
    data[count].get_token() #pulling binop back out again
    return [step[0], (step[1] and exp(data[count].get_token(), data, count))]
  if token == "nil" or token == "false" or token == "true" or String.match(token) or Number.match(token) or token == "'...'":
    return [count, True]
  elif Unop.match(token):
    val = exp(data[count].get_token(), data, count)
    if val[1]:
      return [val[0], True]
    else:
      error("Expected expression after " + token, count)
      return [val[0], False]
  elif re.match(token, "function"):
    #running function funcbody()
    val = funcbody([''], data, count)
    return val
  else:
    return [count, False]
      
  '''
  nil or                    DONE
  false or                  DONE
  true or                   DONE
  Number() or               DONE
  String() or               DONE
  '...' or                  DONE
  function() or
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
    string = "Function: " + x[0]
    if len(x) > 1:
      string = string + ", Parameters: " + x[1]
    for y in x[2:]:
      string = string + ", " + y
    print(string)

def parse(filename):
  global data
  global count
  
  with open(filename) as f:
    data = f.readlines()
  
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