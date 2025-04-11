#
#    Scan a file of Library of Congress subject headings and break complex subject headings
#    like "Word processing--Style manuals" into the individual subject terms, like
#    "Word processing" and "Style manuals".  Optionally output a word list in case it's useful.
#
#    The workflow of which this is a part is described in the accompanying README.md file.
#
#    Usage:  python build-lists.py input-file phrase-file [ word-file ]
#
#    Version:  0.2.0  4/10/25
#
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
# 
import re
import sys

phraseset = set()

wordset = set()
wordsplit = re.compile(r'\W+')

with open(sys.argv[1], encoding="utf-8") as inf:
    for inputline in inf:
        # ignoring line number, LoC number and MARC tag:
        _, _, _, heading = inputline.strip().split(None, 3)  # None ignores multiple spaces
        for phrase in heading.split("--"):
            phraseset.add(phrase)
            for word in wordsplit.split(phrase):
                if word:
                    wordset.add(word)

with open(sys.argv[2], 'w', encoding="utf-8") as phrasefile:
    for phrase in sorted(phraseset):
        print(phrase, file=phrasefile)

if len(sys.argv) == 4:
    with open(sys.argv[3], 'w', encoding="utf-8") as wordfile:
        for word in sorted(wordset):
            print(word, file=wordfile)


