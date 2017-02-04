#time to go to work
# keywords:
# and	break	do	else	elseif
# end	false	for	function	if
# in	local	nil	not	or
# repeat	return	then	true	until	while

#Can either do a backtracking parser or a predictive parser
#Predictive probably the best choice but requires look ahead

def chunk():
  {stat() ';'} #potentially repeats
  [laststat() ';']

def block():
  chunk()

def stat():
  varlist() '=' explist() or
  functioncall() or
  do block() end or
  while exp() do block() end or
  repeat block() until exp() or
  if exp() then block() 
  {elseif exp() then block()} #potentially repeats
  ]else block()] end or
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
  var() {',' var}

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

def main():
  file = open('test.lua', 'r');
  file.read()

if __name__ == "__main__":
  import sys
  parse(sys.argv[1])