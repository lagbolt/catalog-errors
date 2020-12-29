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

with open("lcsh-phrases.txt", 'w', encoding="utf-8") as phrasefile:
    for phrase in sorted(phraseset):
        print(phrase, file=phrasefile)
