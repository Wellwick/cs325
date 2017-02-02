
import re

def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    pass
  
  try:
    import unicodedata
    unicodedata.numeric(s)
    return True
  except (TypeError, ValueError):
    pass
  
  return False


def main():
  #break up the data
  data = ("Read about light, it 121 discounted 115.").split( )
  expr = re.compile('\W|^\.')
  newWord = ""
  
  for word in data:
    #need to check for punctuation
    word = expr.sub('', word)
    #if it's an integer turn into it a char
    if is_number(word):
      word = chr(int(word))
    elif (re.compile('[A-Z]')).match(word) == None: #no changes if it doesn't match
      if len(word) >= 8:
        word = " " + word[3:8]
      elif (re.compile('[aeiou]')).match(word) == None: ##does not start with vowel
        word = word[1:2] + word[:1]
      else:
        word = word[:2]
    
    newWord = newWord + word
      
    
  print(newWord)

if __name__ == "__main__":
    main()