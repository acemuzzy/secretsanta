"""
Usage:
   checkarchive YEAR SENDER

Arguments :
   YEAR - the year to check
   SENDER - the sender to check for
"""

import docopt
import re

arguments = docopt.docopt(__doc__)

year = arguments["YEAR"]
sender = arguments["SENDER"]

regex = re.compile("Pair {}.* ->".format(sender), re.IGNORECASE)

logging_file = "archive" + str(year) + ".txt"
print("\nChecking file {}".format(logging_file))

with open(logging_file, "r") as f:
    for line in f:
        if regex.match(line):
            print "Matched!\n{}".format(line)
            break
    else:
        print "No match found :|"

