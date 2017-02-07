#time to go to work
# keywords:
# and	break	do	else	elseif
# end	false	for	function	if
# in	local	nil	not	or
# repeat	return	then	true	until	while

#Can either do a backtracking parser or a predictive parser
#Predictive probably the best choice but requires look ahead

import re

#regular expressions used 
last = re.compile('return|break')
#a variable or function name must be alphanumeric but not containing only numbers and cannot be a keyword
varFunc = re.compile('function( )*[0-9]*[a-zA-Z_](\w)*\(([0-9]*[a-zA-Z_](\w)*\,( )*)*[0-9]*[a-zA-Z_](\w)*\)')


def chunk(data, count):
  #a chunk can be broken on return or break
  #break can only be used when in a loop
  statementsExecuting = True
  while (statementsExecuting):
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

def laststat(data, count): return count

'''
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


def laststat():
  return [explist()] or
  break

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

def explist():
  {exp() ','} exp()

def exp():
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
        if (varFunc.search(x)):
            print(x)

def parse(filename):
  
  with open(filename) as f:
    data = f.readlines()
  
  #break each line by whitespace characters
  data = [x.strip( ) for x in data]
  
  print(block(data, 0))
  
  #runs if no errors are detected
  printFunctions(data)

if __name__ == "__main__":
  import sys
  try:
    parse(sys.argv[1])
  except IndexError:
    print("Need to provide a lua file to parse")