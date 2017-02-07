import shlex

def main():
  with open("test.lua") as f:
    data = f.read()
   
  #data = [shlex.split(data) for x in data]
  for token in shlex.shlex(data):
    print( repr(token))
  
if __name__ == "__main__":
  main()