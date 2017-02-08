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


def error(string, count):
  global errorsFound
  if (not errorsFound):
    errorsFound = True
    print("Errors found")
   
  #error is passed in as a string with the line number
  count = count + 1 #increase by one since originally accessing array
  print("Error on line ",count,": " + string)

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

def block(data, count):
  return chunk(data, count)

def stat(token, data, count):
  if re.match('function', token):
    #function funcname() funcbody()
    functionName = funcname(data, count)
    count = funcbody(functionName, data, count)
  return count

def laststat(token, data, count): 
  print("LastStat: " + token)
  
  nextToken = data[count].get_token()
  
  if re.match('break', token) and loopDepth == 0:
    #don't decrease loopDepth until we find an end
    if nextToken != None and nextToken != '':
      error("unexpected value after break", count)
      return count
    if loopDepth == 0:
      error("break encoutered not in a loop", count)
      return count
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
    
    '''
    #got to make sure when we find another ' that it isn't an escaped character
    searching = True
    while (searching):
      index = xList[charCount:].find('\'')
      if (index == -1):
        checkErrors()
        print("Expected \' to close string on line ", count+1)
        return
      else:
        if xList[charCount:].find('\\') == index-1 and index != 0:
          #we have found an escaped character
          charCount = charCount + index + 1
        else:
          #have reached the end of the string
          x = xList[1:charCount+index]
          String(x, count)
          xList = xList[charCount+index+1:]
          searching = False
    '''
    
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
  newList.extend(funcName)
  token = data.get_token()
  
  #'(' [parlist()] ')' block() end

def exp(token, data, count):
  nextToken = data[count].get_token()
  data[count].push_token(nextToken)
  if Binop.match(nextToken):
    step = exp(token, [], count)
    data[count].get_token() #pulling binop back out again
    return step and exp(data[count].get_token(), data, count)
  if token == "nil" or token == "false" or token == "true" or Number.match(token) or String.match(token) or token == "'...'":
      return True
  elif Unop.match(token):
    if exp(data[count].get_token(), data, count):
      return True
    else:
      error("Expected expression after " + token, count)
      return False
  else:
    return False
      
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

def function():
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
  
  with open(filename) as f:
    data = f.readlines()
  
  strippedData = []
  for y in data:
      y = shlex.shlex(y)
      strippedData.extend([y])
  
  data = strippedData
  
  print(block(data, 0))
  
  #runs if no errors are detected
  global errorsFound
  if (not errorsFound): printFunctions(data)

if __name__ == "__main__":
  import sys
  try:
    parse(sys.argv[1])
  except IndexError:
    print("Need to provide a lua file to parse")