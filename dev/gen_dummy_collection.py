import re, csv, random, json
import loremipsum as LI

n = 10

path = 'scrap/dummy-collections/'
filename = "collection-"+str(random.randint(1000,9999))
print filename

C = csv.writer(file(path+filename+".csv", 'w'))
C.writerow(('content', 'META_sentences', 'META_words'))

J = {
    "name": " ".join(LI.generate_sentence()[2].split()[:3]),
    "description": LI.generate_sentence()[2],
    "documents": []
}

for a in range(n):
    sentences, words, text = LI.generate_paragraph()
    row = ( text, sentences, words )
    C.writerow(row)

    j = {
        "content" : text,
        "metadata" : {
            "sentences" : str(sentences),
            "words" : str(words),
        }
    }

    J["documents"].append(j)

file(path+filename+".json", 'w').write(json.dumps(J, indent=2))
