#-*- coding: utf-8 -*-

import sys
import os
import re
import sys
import nltk

class Translator:
    def __init__(self):
        self.dictionary = {}
        self.preprocessed = []
        self.translated = []
        self.postprocessed = []

    def preprocess(self, tokenized_sentences):
        f = open(tokenized_sentences, 'r')
        
        for line in f:
            line = line.strip()
            tokens = line.split()

            tokens_processed = []
            prev_word = ()

            for token in tokens:
                # First word
                if prev_word == ():
                    tup = (token.split('/')[0], token.split('/')[1])
                    tokens_processed.append(tup)
                    prev_word = tup

                else:
                    token_word = token.split('/')[0]
                    token_pos = token.split('/')[1]

                    # Combine noun + adjectifying prefix to single adjective
                    if prev_word[1] == 'NNG' and token_pos == 'XSN' and token_word == '\xec\xa0\x81':
                        combined = prev_word[0] + token_word
                        tokens_processed[-1] = (combined, 'VA')

                    # Combine noun + verb prefix to single verb
                    elif prev_word[1] == 'NNG' and token_pos == 'XSV':
                        combined = prev_word[0]
                        tokens_processed[-1] = (combined, 'VV')

                    # Change order for prepositions to come before closest noun (i.e. in desk, in society)
                    elif token_pos == 'JKB':
                        if tokens_processed[-1][1][0] == 'N':
                            tokens_processed.insert(-1,(token_word,token_pos)) 
                    
                    else:
                        tokens_processed.append((token_word, token_pos))
                    prev_word = (token_word, token_pos)

            # Print out a list of words so that their meanings can be looked up on an online dictionary
            for token in tokens_processed:
                # Skip punctuation, numbers, foreign characters, etc.
                if token[1] not in ["SF", "SP", "SS", "SE", "SO", "SL", "SW", "SN"]:
                    self.dictionary[token[0]] = []
            self.preprocessed.append(tokens_processed)

        f2 = open("./data/list_of_tokens.txt", 'w')
        f2.seek(0)
        for key in self.dictionary.keys():
            f2.write(str(unicode(key)) + ":\n")

        f.close()
        f2.close()


    def importDictionary(self, dictionary_file):
        f = open(dictionary_file, 'r')

        brown_a = nltk.corpus.brown.tagged_sents()
        unigram_tagger = nltk.UnigramTagger(brown_a)

        for line in f:
            line = line.strip()
            entries = line.split(':')
            #print entries

            word = entries[0]
            
            if len(entries) > 1 and len(entries[1]) > 1:
                meanings = entries[1].split(',')
                annotated_meanings = unigram_tagger.tag(meanings)

                print annotated_meanings
                if word in self.dictionary:
                    self.dictionary[word] = annotated_meanings
                #else:
                #    print str(unicode(word)) # for debugging
                

    ### TO DO: CHOOSE THE RIGHT TRANSLATION AMONG MANY
    def translate(self):
        for sentence in self.preprocessed:
            translated_sentence = []
            for token in sentence:
                korean_word = token[0]
                korean_pos = token[1]

                # Directly paste punctuation, numbers, foreign characters, etc.
                if korean_pos in ["SF", "SP", "SS", "SE", "SO", "SL", "SW", "SN"]:
                    translated_sentence.append(korean_word)

                # Tag plural suffix to previous word
                elif korean_pos == 'XSN' and korean_word == '\xeb\x93\xa4':
                    translated_sentence[-1] = translated_sentence[-1] + '<PLURAL>'

                # Tag possessive(genitive) case marker to previous word
                elif korean_pos == 'JKG':
                    translated_sentence[-1] = translated_sentence[-1] + '<POSSESSIVE>'

                # Tag objective case marker to previous word
                elif korean_pos == 'JKO':
                    translated_sentence[-1] = translated_sentence[-1] + '<OBJECT>'

                # Tag subjective case marker to previous word
                elif korean_pos == 'JKS':
                    translated_sentence[-1] = translated_sentence[-1] + '<SUBJECT>'

                # Tag "be" words
                elif korean_pos == 'VCP':
                    translated_sentence.append('<POSITIVE BE>')
                elif korean_pos == 'VCN':
                    translated_sentence.append('<NEGATIVE BE>')

                # Tag negative
                elif korean_word == '\xec\x97\x86' or korean_word == '\xec\x95\x8a':
                    translated_sentence.append('<NEGATION>')

                # skip parts of speech (Korean endings) that do not have English counterparts
                elif korean_pos[0] == 'E':
                    pass;

                else:
                    english_translations = self.dictionary[korean_word]
                    #print english_translations

                    if len(english_translations) > 0:
                        found = False
                        for t in english_translations:
                            # pick verb English translations for original Korean verbs / proper nouns / adjectives / common nouns / adjectives
                            if (t[1] == 'VB' and korean_pos == 'VV') or \
                            (t[1] == 'NP' and korean_pos == 'NNP') or \
                            (t[1] == 'JJ' and korean_pos == 'VA') or \
                            (t[1] == 'NN' and korean_pos[:2] == 'NN') or \
                            (t[1] == 'RB' and korean_pos == 'MA'):
                                translated_sentence.append(t[0])
                                found = True
                                break
                        if not found:
                            translated_sentence.append(english_translations[0][0])
                    #else:
            self.translated.append(translated_sentence)

    
    ### TO DO: PREPROCESS TRANSLATED SENTENCES (correct grammar, reorder)
    def postprocess(self):
        for sentence in self.translated:
            sentence[0] = sentence[0].capitalize()

            self.postprocessed.append(sentence)
            printSentences(sentence)



def loadList(file_name):
    """Loads corpus as lists of lines. """
    with open(file_name) as f:
        l = [line.strip() for line in f]
    return l

def printSentences(sentences):
    print ' '.join(sentences)

def main():
    tokenized_file = "./data/dev-tokenized.txt"
    dictionary_file = "./data/dict.txt"

    t = Translator()
    t.preprocess(tokenized_file)

    t.importDictionary(dictionary_file)
    t.translate()
    t.postprocess()

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    main()
