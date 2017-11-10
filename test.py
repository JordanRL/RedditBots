import re

# testSubject = "User: 12Ed93 | Ban | Threshold: 1"
testSubject = "blah blah blah"
testExpr = r"User: (.*?) \| (.*?) \| Threshold: ([0-9].?)"

searchObj = re.search(testExpr, testSubject)
print(searchObj.group(1))
print(searchObj.group(2))
print(searchObj.group(3))
