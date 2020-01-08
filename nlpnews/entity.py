from collections import defaultdict
from afinn import Afinn
import pandas as pd 
import nltk
from nltk import word_tokenize, pos_tag
from  nlpnews import article

SCORE_LIMITER = -0.5

def get_entities():

    afinn = Afinn()
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    entities = []

    for op in article.opinions():
        print("Investigating article: ", op.title)
        # Split to sentences and pos-tag them
        sentences = tokenizer.tokenize(op.fulltext)
        tagged_words = []
        for sent in sentences:
            tagged_words += pos_tag(word_tokenize(sent))

        # Keep track of last noun in text
        # And if there is a verb between noun and target negative word.
        # Reason: If there is a verb and then negative word is a noun,
        # then then previous noun before that is likely the negative entity 
        last_noun = None
        check_for_multipart = False
        verb_after = False
        previous_sentence_noun = False
        
        for word, tag in tagged_words:
            score = afinn.score(word)

            # If negative and NN*, then there needs to be a verb
            # between this and the noun
            if score < SCORE_LIMITER and tag.startswith("NN"):
                if last_noun and verb_after:
                    entities.append(last_noun)
                
                last_noun = None
                verb_after = False
                check_for_multipart = False

            elif score < SCORE_LIMITER and (tag.startswith("JJ") or tag.startswith("VB")):
                if last_noun:
                    entities.append(last_noun)

                last_noun = None
                verb_after = False
                check_for_multipart = False

            elif tag.startswith("NNP") and len(word) > 1:
                # If the previous tag was also noun, they belong together 
                if check_for_multipart:
                    last_noun += " " + word
                else:
                    last_noun = word

                check_for_multipart = True

            elif tag.startswith("VB"):
                if last_noun is not None:
                    verb_after = True
            
                check_for_multipart = False
            
            # If there is a full stop, move noun to previous_sentence_noun
            # That can be "woken up" by a preposition
            elif word == ".":
                previous_sentence_noun = last_noun
                last_noun = None

                check_for_multipart = False

            elif word.startswith("PR"):
                last_noun = previous_sentence_noun
                previous_sentence_noun = None
                check_for_multipart = False

            else:
                check_for_multipart = False
    
    # Put entities in a dictionary with mention counts

    entitydict = defaultdict(int)

    for ent in entities:
        entitydict[ent] +=1
    
    entitydict = {k:v for k, v in sorted(entitydict.items(), key=lambda x: -x[1])}

    df = pd.DataFrame(list(zip(entitydict.keys(), entitydict.values())), columns=["token", "count"])
    df.to_csv("./dataframes/entities.csv")

    return entitydict


