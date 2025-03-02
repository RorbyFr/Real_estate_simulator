import re
import sys


f = sys.argv[1]

# Read file given in argument from batch
with open(f, "r", encoding="utf-8") as file:
    d = file.read()

# Delete `u` prefix behind characters
d = re.sub(r'u"([^"]+)"', r'"\1"', d)

# Delete "None" use in QCoreApplication.translate()
d = re.sub(r'QCoreApplication.translate\((.*?),\s*"(.*?)",\s*None\)', r'QCoreApplication.translate(\1, "\2")', d)

# Overflow file
with open(f, "w", encoding="utf-8") as file:
    file.write(d)

