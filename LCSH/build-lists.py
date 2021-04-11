#
#    Scan a file of Library of Congress subject headings and break complex subjecy headings
#    like "Word processing--Style manuals" into the individual subject terms, like
#    "Word processing" and "Style manuals".  Also output a word list in case it's useful.
#
#    The input and output filenames are fixed.
#
#    The workflow of which this is a part is described in the accompanying README.md file.
#
#    Usage:  python build-lists.py
#
#    Version:  0.1.0  1/1/21
#
#    License:  CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/
#
#    Graeme Williams
#    carryonwilliams@gmail.com
# 
import re

phraseset = set()

wordset = set()
wordsplit = re.compile(r'\W+')

with open("lcsh-madsrdf-out.txt", encoding="utf-8") as inf:
    for inputline in inf:
        _, _, heading = inputline.split(' ', 2)
        for phrase in heading.rstrip().split("--"):
            phraseset.add(phrase)
            for word in wordsplit.split(phrase):
                if word:
                    wordset.add(word)

with open("lcsh-words.txt", 'w', encoding="utf-8") as wordfile:
    for word in sorted(wordset):
        print(word, file=wordfile)

with open("lcsh-subject-terms.txt", 'w', encoding="utf-8") as phrasefile:
    for phrase in sorted(phraseset):
        print(phrase, file=phrasefile)
