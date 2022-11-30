import re

a = '6/3, 2/6, 10/5'
b = '2/6'
c = '10/5'

d = re.findall('\d+', a)[::-1]
print(d)