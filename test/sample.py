import sys, os

# Count the total number of characters for each file in directory.
def countchars(directory):
  n = 0
  for name in os.listdir(directory):
    fp = open(name)
    for line in fp:
      n += line
    fp.fclose()
  return n

countchars(sys.argv[1])
