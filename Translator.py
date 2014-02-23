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

    def preprocess(self, tokenized_sentences):
        f = open(tokenized_sentences, 'r')

        for line in f:
            line = line.strip()
            tokens = line.split()
            tokens_processed = [(token.split('/')[0], token.split('/')[1]) for token in tokens]

            # print out a list of words so that their meanings can be looked up on an online dictionary
            f2 = open("./data/list_of_tokens.txt", 'w')
            f2.seek(0)
            for token in tokens_processed:
                self.dictionary[token[0]] = []
            for key in self.dictionary.keys():
                f2.write(str(unicode(key)) + ":\n")
            f2.close()

            self.preprocessed.append(tokens_processed)
        f.close()

    def importDictionary(self, dictionary_file):
        f = open(dictionary_file, 'r')

        for line in f:
            line = line.strip()
            entries = line.split(':')
            #print entries

            word = entries[0]
            
            if len(entries) > 1 and len(entries[1]) > 1:
                meanings = entries[1].split(',')
                if len(meanings) > 1:
                    annotated_meanings = [(meaning, nltk.pos_tag([meaning])) for meaning in meanings]
                else:
                    english_pos = nltk.pos_tag([entries[1]])
                    annotated_meanings = [(entries[1],english_pos)]

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

                if korean_pos in ["SF", "SP", "SS", "SE", "SO", "SL", "SW", "SN"]:
                    translated_sentence.append(korean_word)
                else:
                    english_translations = self.dictionary[korean_word]
                    #print english_translations

                    if len(english_translations) > 0:
                        #translated_sentence.append(korean_pos)
                    #else:
                        translated_sentence.append(english_translations[0][0])
            self.translated.append(translated_sentence)
            printSentences(translated_sentence)

    
    ### TO DO: PREPROCESS TRANSLATED SENTENCES (correct grammar, reorder)
    def postprocess(self):
        pass


def loadList(file_name):
    """Loads corpus as lists of lines. """
    with open(file_name) as f:
        l = [line.strip() for line in f]
    return l

def printSentences(sentences):
    print ' '.join(sentences)

def main():
    reload(sys)
    sys.setdefaultencoding('utf-8')
    
    tokenized_file = "./data/dev-tokenized.txt"
    dictionary_file = "./data/dict.txt"

    t = Translator()
    t.preprocess(tokenized_file)

    t.importDictionary(dictionary_file)
    t.translate()
    #t.postprocess()

if __name__ == '__main__':
    main()
