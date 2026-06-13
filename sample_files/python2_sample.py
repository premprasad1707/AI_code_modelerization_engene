# Sample Python 2 code
print "Hello, Legacy World"

xrange_values = xrange(5)

try:
    file_obj = open('demo.txt')
except Exception, e:
    print e

name = raw_input("Enter name: ")

def divide(a, b):
    return a / b

for i in xrange_values:
    print i
