import nltk
import numpy
import re


nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("maxent_ne_chunker")
nltk.download("words")

# open files
article = open("/home/anooj/raghuBlogSearch/scraperpipeline/management/commands/extractBlogFeatures/docs/article3.txt", "r").read()
countries = set(line.strip().lower() for line in open("/home/anooj/raghuBlogSearch/scraperpipeline/management/commands/extractBlogFeatures/docs/countries.txt", "r"))

Indian = open("/home/anooj/raghuBlogSearch/scraperpipeline/management/commands/extractBlogFeatures/docs/India.txt", "r").read()
American = open("/home/anooj/raghuBlogSearch/scraperpipeline/management/commands/extractBlogFeatures/docs/USA.txt", 'r').read()
Japanese = open("/home/anooj/raghuBlogSearch/scraperpipeline/management/commands/extractBlogFeatures/docs/Japan.txt", 'r').read()
Russian = open("/home/anooj/raghuBlogSearch/scraperpipeline/management/commands/extractBlogFeatures/docs/Russia.txt", 'r').read()
article2 = open("/home/anooj/raghuBlogSearch/scraperpipeline/management/commands/extractBlogFeatures/docs/test.txt", 'r').read()
num = open("/home/anooj/raghuBlogSearch/scraperpipeline/management/commands/extractBlogFeatures/docs/num.txt", 'r').read()

nameToCountryMap = {}
with open("/home/anooj/raghuBlogSearch/scraperpipeline/management/commands/extractBlogFeatures/docs/name2lang.txt") as f:
    for line in f:
        temp = line.split(",")
        name = temp[0].strip()
        country = temp[1].strip()
        nameToCountryMap[name] = country



# Return a list of all country names and nationalities('American', 'Indian')
def extractPlaces(text):
    sent = nltk.tokenize.word_tokenize(text)
    pos_tag = nltk.pos_tag(sent)
    namedEntities = nltk.ne_chunk(pos_tag)
    places = []

    for namedEntity in namedEntities:
        if type(namedEntity ) == nltk.tree.Tree:
            if namedEntity .label() == "GPE":
                places.append(u" ".join([i[0] for i in namedEntity.leaves()]))

    return places


def extractCountries(text):
    sent = nltk.tokenize.word_tokenize(text)
    pos_tag = nltk.pos_tag(sent)
    namedEntities = nltk.ne_chunk(pos_tag)
    countriesList = []

    for namedEntity in namedEntities:
        if type(namedEntity ) == nltk.tree.Tree:
            if namedEntity .label() == "GPE":
                placeName = (u" ".join([i[0] for i in namedEntity.leaves()]))
                if placeName in countries:
                    print ("inserting " + placeName + " into countries")
                    countriesList.append(placeName)

    return countriesList




# Returns a list of all humans names in text
def extractNames(text):
    sent = nltk.word_tokenize(text)
    pos_tag = nltk.pos_tag(sent)
    namedEntities = nltk.ne_chunk(pos_tag)
    res = []
    for namedEntity  in namedEntities:
        if type(namedEntity ) == nltk.tree.Tree:
            if namedEntity .label() == "PERSON":
                res.append(u" ".join([i[0] for i in namedEntity.leaves()]))

    return res


#Extracts humans names and returns their respective country
def nameToCountry(text):
    names = []
    nameToCountryPairs = []
    namedEntities = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(text)))
    for namedEntity in namedEntities:
        if type(namedEntity ) == nltk.tree.Tree:
            if namedEntity .label() == "PERSON":
                name = f" ".join(i[0] for i in namedEntity.leaves())
                names.append(name)

    for name in names:
        tokens = name.split(" ")
        found = False
        for token in tokens:
            if token in nameToCountryMap:
                nameToCountryPairs.append((name, nameToCountryMap[token]))
                found = True
                break
        if found == False:
            nameToCountryPairs.append((name, 'Not identified'))
    return nameToCountryPairs

#regex pattern to find all numbers in the text
def numbers(rtext):
    out = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", rtext)
    return out


#pytest for extracting names
def testAnswer1():
    assert extractNames(Indian) == ['Satya', 'Narayana Nadella']
def testAnswer2():
    assert extractNames(American) == ['Marques', 'Keith Brownlee']
def testAnswer3():
    assert extractNames(Japanese) == ['Makoto', 'Makoto Shinkai']
def testAnswer4():
    assert extractNames(Russian) == ['Garry', 'Kimovich Kasparov']
def testAnswer5():
    assert nameToCountry(article2) == [('Helmut Kohl', 'German'), ('Satya Narayana Nadella', 'Not identified'), ('Garry Kimovich Kasparov', 'Russian'), ('Marques Keith Brownlee', 'English'), ('Makoto Niitsu', 'Not identified'), ('Makoto Shinkai', 'Not identified')]
def testAnswer6():
    assert numbers(num) == ['8', '15', '2022.', '8.5', '2030', '9.7', '2050', '10.4', '2100.', '72.8', '2019', '9', '1990.', '77.2', '2050.']


