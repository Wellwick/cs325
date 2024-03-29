#time to go to work

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
funcNames = []
paramlist = []


#regular expressions used 
last = re.compile('^(return|break)$')
#a variable or function name must be alphanumeric but not containing only numbers and cannot be a keyword, cannot start with a digit
Keyword = re.compile('^((and)|(break)|(do)|(else)|(elseif)|(end)|(false)|(for)|(function)|(if)|(in)|(local)|(nil)|(not)|(or)|(repeat)|(return)|(then)|(true)|(until)|(while))$')
varFuncName = '^[a-zA-Z_](\w)*$'
Name = re.compile(varFuncName)
Number = re.compile('^(([0-9]+(\.[0-9]*)?)|(\.[0-9]+))$')
String = re.compile('^((\".*\")|(\'.*\'))$')
Binop = re.compile('^((\+)|(\-)|(\*)|(\/)|(\^)|(\%)|(\.\.)|(\<)|(\<\=)|(\>)|(\>\=)|(\=\=)|(\~\=)|(and)|(or))$')
Unop = re.compile('^((\-)|(not)|(\#))$')
Ellipse = re.compile('^(\.\.\.)$')
LongString = re.compile('(\[(=)*\[)')

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
  print("Error on line",newCount,": " + string)

#can only afford to do once or line number is lost
def returnToken(token):
  global data
  global count
  data[count].push_token(token)

def getNextToken():
  global data
  global count
  if not count < len(data):
    return False
  token = data[count].get_token()
  while token == None or token == '':
    count = count + 1
    if count >= len(data):
      #this means we have reached the end of the file
      count = count - 1
      return False
    token = data[count].get_token()
  
  if token == '<' or token == '=' or token == '>' or token == '~':
    #try and get another token
    secondToken = viewNextToken()
    if secondToken != False and secondToken == '=': #this is a binop
      secondToken = getNextToken()
      token = token + secondToken
  elif token == '.':
    #may have to pull out another two values
    secondToken = viewNextToken()
    if secondToken != False and (secondToken == '..' or secondToken == '.'):
      secondToken = getNextToken()
      token = token + secondToken
  
  return token

#pops and then replaces the next token, retains same line position
def viewNextToken():
  global data
  global count
  newCount = count
  if not count < len(data):
    return False
  token = data[newCount].get_token()
  while token == None or token == '':
    newCount = newCount + 1
    if newCount >= len(data):
      #this means we have reached the end of the file
      return False
    token = data[newCount].get_token()
  
  newToken = token
  
  if token == '<' or token == '=' or token == '>' or token == '~':
    #try and get another token
    secondToken = viewNextToken()
    if secondToken != False and secondToken == '=': #this is a binop
      newToken = token + secondToken
  elif token == '.':
    #may have to pull out another two values
    secondToken = viewNextToken()
    if secondToken != False and (secondToken == '..' or secondToken == '.'):
      newToken = token + secondToken
  
  data[newCount].push_token(token)
  return newToken

def chunk():
  #a chunk can be broken on return or break
  #break can only be used when in a loop
  global count
  statementsExecuting = True
  token = True
  while (token != False):
    token = getNextToken()
    #if token != False: #debug 
    #  print("Line",count,":" + token)
    if token != False and last.match(token):
      laststat(token)
    elif token != False and (token == 'end' or token == 'elseif' or token == 'else'):
      return token
    elif token != False and not re.match(';', token):
      # ';' can be skipped, so treating it as an empty statement
      stat(token)
      
  return False

def block():
  return chunk()

'''
def stat():
  varlist() '=' explist() or
  functioncall() or
  do block() end or                                         DONE!
  while exp() do block() end or
  repeat block() until exp() or
  if exp() then block()                                     DONE!
  {elseif exp() then block()} #potentially repeats          DONE!
  [else block()] end or                                     DONE!
  for Name() '=' exp ',' exp [',' exp] do block() end or    DONE!
  for namelist() in explist() do block() end or             DONE!
  function funcname() funcbody() or                         Funcbody needs completion
  local function Name() funcbody() or                       DONE!
  local namelist() ['=' explist()]                          DONE!
'''

def stat(token):
  global loopDepth
  if token == 'function':
    #function funcname() funcbody()
    #print("FOUND FUNCTION") #debug
    functionName = funcname()
    funcbody(functionName)
  elif token == 'for':
    token = getNextToken()
    if token == False:
      return
    if Name.match(token) and not Keyword.match(token):
      nextToken = viewNextToken()
      if nextToken == '=':
        #looking for exp, exp, [, exp]
        getNextToken()
        token = getNextToken()
        if token == False or not exp(token, False):
          error("Expected expression after '=' in for statement")
          return
        
        token = getNextToken()
        if token == False or token != ',':
          error("Expected ',' after expression in for statement")
          return
        
        token = getNextToken()
        if token == False or not exp(token, False):
          if token != False:
            error("Expected expression after ',' in for statement, instead got " + token)
          else:
            error("Expected expression after ',' in for statement, instead encountered end of file")
          return
        
        token = getNextToken()
        #print("Starting for loop: " + token) #debug
        if token == False or token == ',':
          #want another expression
          token = getNextToken()
          if token == False or not exp(token, False):
            error("Expected expression after ',' in for statement")
            return
          
          token = getNextToken()
          
      elif nextToken == ',' or nextToken == 'in':
        #expecting namelist in explist
        token = namelist(token)
        if token == False or token != 'in':
          if token != False:
            error("Expected 'in' for 'for' loop, encountered " + token)
          else:
            error("Expected 'in' for 'for' loop, encountered end of file")
          return
        
        token = getNextToken()
        if explist(token) == False: 
          return
        token = getNextToken()
      
      #completed the differentiation for 
      if token == False or token != 'do':
        if token != False:
          error("Expected 'do' to lead into for block, instead received " + token)
        else:
          error("Expected 'do' to lead into for block, instead received end of file")
        return
      
      #need to increase loopDepth
      loopDepth = loopDepth + 1
      token = block()
      
      if token == False or token != 'end':
        #failed at producing for loop
        error("Expected end to catch bottom of for loop")
      
      #decrease loopDepth again
      loopDepth = loopDepth - 1
    
  elif token == 'do':
    #process a block and corresponding end
    token = block()
    if token == False or token != 'end':
      error("Expencted end to finish do block")
  elif token == 'if':
    #next comes an expression
    token = getNextToken()
    if token == False or not exp(token, False):
      error("Was expecting expression after 'if'")
      return
    
    token = getNextToken()
    if token == False or token != 'then':
      error("Was expecting 'then' after expression in 'if' clause")
      return
    
    val = block()
    if val == False:
      error("Was expecting 'end' for if statement")
      return
    elif val == 'end':
      return
    
    while val == 'elseif':
      #perform this on a loop if elseifs continue to appear
      token = getNextToken()
      if token == False or not exp(token, False):
        error("Was expecting expression after 'elseif'")
        return
      
      token = getNextToken()
      if token == False or token != 'then':
        error("Was expecting 'then' after expression in 'elseif' clause")
        return
      val = block()
      if val == False:
        error("Was expecting 'end' for if statement")
        return
      elif val == 'end':
        return
      
    if val == 'else':
      val = block()
      if val == False:
        error("Was expecting 'end' for if statement")
        return
      elif val == 'end':
        return
  elif token == 'while':
    #looking for expression followed by 'do'
    token = getNextToken()
    if token == False or not exp(token, False):
      error("Was expecting expression after 'while'")
      return
    
    token = getNextToken()
    
    if token == False or token != 'do':
      error("Was expecting 'do' after expression")
      return
    
    #need to increase loopDepth
    loopDepth = loopDepth + 1
    token = block()
    
    if token == False or token != 'end':
      #failed at producing for loop
      error("Expected end to catch bottom of while loop")
      
    #decrease loopDepth again
    loopDepth = loopDepth - 1
    
  elif token == 'local':
    token = getNextToken()
    if token == False or (token != 'function' and not Name.match(token)):
      error("Expected function or namelist")
      return
    elif token == 'function':
      token = getNextToken()
      if token == False or not Name.match(token):
        if token != False:
          error("Expected a name for the function, instead recieved " + token)
        else:
          error("Expected a name for the function, instead recieved end of file")
        return
      
      #now build funcbody()
      funcbody(token)
    else: #will result when there is a namelist
      token = namelist(token)
      if token != False:
        if token == '=':
          explist(getNextToken())
        else:
          returnToken(token)
          
  elif token == '(' or (Name.match(token) and not Keyword.match(token)):
    #we are looking at varlist or a functioncall, both of which can reach out to prefixexp
    #since these are only constructed in stat, import varlist here
    value = prefixexp(token)
    if value == 'var':
      token = getNextToken()
      broken = False
      while token == ',':
        token = getNextToken()
        if token == False or prefixexp(token) != 'var':
          error("Expected variable declared after ,")
          broken = True
        token = getNextToken()
      
      if token == False:
        error("Unexpectedly reached end of file")
        return
      
      if token != '=':
        error("Expected assignment of variable(s) instead of " + token)
      elif not broken:
        token = getNextToken()
        explist(token)
    elif value != 'funccall':
      #expected a function call
      error("Expected a function call or variable assignment")
  else:
    if token != False:
      error("Was expecting statement to begin at " + token)
    else:
      error("Was expecting statement to begin at end of file")

def laststat(token):
  #print("LastStat: " + token) #debug
  global loopDepth
  if re.match('break', token):
    #don't decrease loopDepth until we find an end
    if loopDepth == 0:
      error("break encountered not in a loop")
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
    if token == False or not exp(token, False):
      #reached end of expression list
      if expectingExpression:
        error("Expected expression after ,")
        returnToken(token)
        return False
      return token
    
    #after the checking is finished, clean for next round of exp() removal
    lastToken = token
    token = viewNextToken()
    if token != False and token == ',':
      getNextToken()
      token = getNextToken()
      expectingExpression = True
    else:
      return True
  
  return True
  #{exp() ','} exp()

def funcname():
  # can just be a sequence of names
  token = getNextToken()
  if token == False or (not Name.match(token)) or Keyword.match(token):
    error("Expected function name")
    return [False]
  else:
    return [token]
  #Name() {',' Name()} [':' Name()]

def funcbody(funcName):
  newList = []
  if funcName[0] != False: #can occur if this a new expression
    newList.extend([funcName])
  token = getNextToken()
  #expection parenthesis
  if token == False or token != '(':
    error("Expecting parenthesis for function")
    return False
  
  global paramlist
  paramlist = []
  token = getNextToken()
  if token == False:
    error("Expecting parenthesis closing for function, encountered end of file")
    return False
  elif token != ')':
    #got a parlist()
    parlist(token, newList)
    
  #once this point is reached then the parameters have been entered
  if funcName[0] == False:
    funcName = [""]
  elif len(paramlist) > 0:
    for parameter in paramlist:
      newList.extend(parameter)
  token = block()
  
  if token != False and token == 'end':
    #print("Function " + funcName[0] + " was completed") #debug
    funcNames.extend([newList])
    #print(newList) #debug
    return True
  else:
    if len(funcName) > 0:
      error("Function " + funcName[0] + " was not generated because end could not be found")
    else:
      error("Function was not generated because end could not be found")
    return False
  #'(' [parlist()] ')' block() end

def parlist(token, newList):
  global paramlist
  if not Ellipse.match(token):
    token = namelist(token)
    if token != False and token == ',':
      #we expect the next symbol to be an ellipse
      token = getNextToken()
      if token == False or not Ellipse.match(token):
        error("Expecting ellipse at final value")
      else:
        paramlist.extend('...')

def namelist(token):
  global paramlist
  while token != False and (Name.match(token) and not Keyword.match(token)):
    paramlist.extend(token)
    token = getNextToken()
    if token == False or token != ',':
      #reached the end of the namelist
      return token
    else:
      token = getNextToken()
  
  #if it is possible to escape the while list, there has been an error 
  #unless the token is an ellipse
  if token == False or not Ellipse.match(token):
    error("Expected variable name")
  return token
  
def exp(token, foundBinop):
  nextToken = viewNextToken()
  
  if nextToken != False and Binop.match(nextToken) and not foundBinop:
    step = exp(token, True)
    x = getNextToken() #pulling binop back out again
    #print("Found a binop expression match " + x) #debug command
    newToken = getNextToken()
    if newToken == False:
      error("Expected expression, recieved end of file")
      return
    step2 = exp(newToken, False)
    return (step != False and step2 != False)
  if token == "nil" or token == "false" or token == "true" or String.match(token) or Number.match(token) or token == "...":
    return True
  elif Unop.match(token):
    val = exp(getNextToken(), False)
    if val:
      return True
    else:
      error("Expected expression after " + token)
      return False
  elif token == "function":
    #running function funcbody()
    val = funcbody([False])
    return val
  elif token == '(' or (Name.match(token) and not Keyword.match(token)):
    #constructing a prefixexp
    return prefixexp(token)
  elif token == '{':
    return tableconstructor(token)
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
  prefixexp() or            DONE
  tableconstructor() or     DONE
  exp() binop() exp() or    DONE
  unop() exp()              DONE
  '''

def prefixexp(token):
  #either a var, functioncall or '(' exp() ')'
  #this gets confusing however since all three can recall prefixexp
  #needs forward checking
  #potential follow set of prefixexp is '[', '.', ':', '(' for single step removal
  #as an expression can also have ',', Binop, ']', ')', ';'
  if token == '(':
    token = getNextToken()
    if token != False and token == ')':
      return 'funccall'
    
    correct = explist(token)
    if correct != False:
      token = getNextToken()
      correct = 'funccall'
    else:
      token = getNextToken()
    if token == False or token != ')':
      error("Expected closing bracket for prefixed expression")
      correct = False
    
    return correct
  elif Name.match(token) and not Keyword.match(token):
    #will either be a var or a function call, but no way to check this without recursion.
    #consume token for the Name construction
    token = viewNextToken()
    correct = 'var'
    #there can be a recursive prefixexp
    while token != False and (token == '(' or (Name.match(token) and not Keyword.match(token))):
      token = getNextToken()
      if correct != False:
        correct = prefixexp(token)
      token = viewNextToken()
    
    if token == False:
      #you have output a variable name!
      return correct
    elif token == '[':
      getNextToken()
      #this method will encapsulate part of var
      token = getNextToken()
      if token == False or not exp(token, False):
        if token != False:
          error("Expected expression to occur at " + token)
        else:
          error("Expected expression, encountered end of file")
        return False
      token = getNextToken()
      if token == False or token != ']':
        error("Expected to close [ ... ] brackets")
        return False
      else:
        return 'var'
    elif token == '.':
      getNextToken()
      #another var method
      token = getNextToken()
      if token == False or not (Name.match(token) and not Keyword.match(token)):
        error("Expected name to be made!")
        return False
      else: return 'var'
    elif token == ':' or token == '(' or token == '{' or String.match(token):
      #building a funccall
      getNextToken()
      if token == ':':
          
        token = getNextToken()
        if token == False:
          error("Expected a variable name, encountered end of file")
          return False
        elif not Name.match(token):
          error("Expected a variable name, encountered " + token + " file")
          return False
          
        nextToken = getNextToken()
        if nextToken == False or (token != '(' and token != '{' and not String.match(token)):
          if token != False:
            error("Expected to build args after " + token)
          else:
            error("Expected to build args, encountered end of file")
          return False
          
      args(token)
    else:
      #totally acceptable to just output a variable name
      return correct
    
  else:
    if token != False:
      error("Expected prefixed expression on " + token)
    else:
      error("Expected prefixed expression, encountered end of file")
    return False
  
def args(token):
  if token == '(':
    token = getNextToken()
    if token == False:
      error("Failed to build args because end of file reached")
      return
    
    if token != ')':
      if explist(token) == False:
        return
      token = getNextToken()
      if token == False: return
    
    if token != ')':
      error("Expected closing bracket for arguements, instead encountered " + token)
      
  elif token == '{':
    tableconstructor(token)
      

def tableconstructor(token):
  if token != '{': return False
  
  token = getNextToken()
  if token == False:
    error("Failed to build table, reached end of file")
    return False
  
  while token != '}':
    if field(token) == False:
      return False
    token = getNextToken()
    if token != False and (token == ',' or token == ';'):
      token = getNextToken()
    
    if token == False:
      error("Failed to build table, reached end of file expecting '}'")
      return False
    
  if token == '}':
    return True
  else:
    error("Expected '}', recieved " + token)
    return False
    
    
def field(token):
  if token == '[':
    # [ exp ] = exp
    token = getNextToken()
    if token == False or not exp(token):
      if token != False:
        error("Failed to build table, couldn't build expression starting at " + token)
      else:
        error("Failed to build table, reached end of file")
      return False
    
    token = getNextToken()
    if token == False or token != ']':
      if token != False:
        error("Failed to build table, was expecting ']', recieved " + token)
      else:
        error("Failed to build table, reached end of file")
      return False
    
    token = getNextToken()
    if token == False or token != '=':
      if token != False:
        error("Failed to build table, was expecting '=', recieved " + token)
      else:
        error("Failed to build table, reached end of file")
      return False
    
    
    token = getNextToken()
    if token == False or not exp(token):
      if token != False:
        error("Failed to build table, couldn't build expression starting at " + token)
      else:
        error("Failed to build table, reached end of file")
      return False
    
    return True
  elif Name.match(token):
    token = getNextToken()
    if token == False or token != '=':
      if token != False:
        error("Failed to build table, was expecting '=', recieved " + token)
      else:
        error("Failed to build table, reached end of file")
      return False
    
    token = getNextToken()
    if token == False or not exp(token):
      if token != False:
        error("Failed to build table, couldn't build expression starting at " + token)
      else:
        error("Failed to build table, reached end of file")
      return False
    
    return True
    
  elif not exp(token):
    error("Did not get field at " + token)
    return False
  else:
    return True
'''

def varlist():        DONE - HANDLED IN STAT
  #var() {',' var()}

def var():            CAPTURED WITHIN PREFIXEXP
  Name() or
  prefixexp() '[' exp() ']' or
  prefixexp() '.' Name


def prefixexp():      MOSTLY DONE, need to make sure we check for ([explist]) only after a single recursion
  var() or
  functioncall() or
  '(' exp() ')'

def functioncall():         HANDLED IN PREFIXEXP mostly
  prefixexp() args() or
  prefixexp() ':' Name() args()

def args():                 MOSTLY DONE on prefixexp()
  '(' [explist()] ')' or
  tableconstructor() or
  String()

def function():         <In Progress>
  function funcbody()

def tableconstructor():                         DONE
  '{' [fieldlist()] '}'

def fieldlist():                                DONE
  field() {fieldsep() field()} [fieldsep]

def field():                                    DONE
  '[' exp() ']' '=' exp() or
  Name() '=' exp() or
  exp()

def fieldsep():                                 HANDLED IN fieldlist
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
          thisLine = line[:startIndex] + '"\''
          
          while index < len(line):
            if line[index] == '"':
              thisLine = thisLine + "\\\""
            elif outerExpr.match(line[index:]):
              thisLine = thisLine + '\'"'
              index = index + len(outerCatch) - 2
              thisLine = thisLine + line[index:]
              outerCatch = False
              break
            else:
              thisLine = thisLine + line[index]
            index = index + 1
          
          if outerCatch != False:
            error("Expected " + outerCatch + " by the end of the line")
            data[count] = thisLine + '""' #treat as empty string so we can continue parsing
          else:
            #need to save the data
            data[count] = thisLine
            checked = False
            #print(thisLine)
            break
          #no change to count so that it checks through another time in case there are other 
          #long strings
            
        index = index + 1
    else:
      count = count + 1
  
  #reset count before we go back
  count = 0
  return data

def parse(filename):
  global data
  global count
  
  with open(filename) as f:
    data = f.readlines()
  
  data = parseLongStrings(data)
  
  strippedData = []
  for y in data:
      y = shlex.shlex(y, posix=True)
      strippedData.extend([y])
  
  data = strippedData
      
  block()
  if count < len(data) - 1:
    error("Did not reach the bottom of the file")
  
  #runs if no errors are detected
  global errorsFound
  if (not errorsFound): printFunctions(data)

if __name__ == "__main__":
  import sys
  try:
    parse(sys.argv[1])
  except IndexError:
    print("Need to provide a lua file to parse")