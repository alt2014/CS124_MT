
import sys
import os
import re

class Translator:
    def __init__(self):


    def translate(self, corpus_sentences):
    
    return #list of English sentences, translated word-tow-rd

    def annotate(self, translated_sentences):

    return #list of sentences, annotated

    def postprocess(self, annotated_sentences):

    return #list of sentences, postprocessed


def loadList(file_name):
    """Loads corpus as lists of lines. """
    with open(file_name) as f:
        l = [line.strip() for line in f]
    return l

def main():
    corpus_file = "../data/..."
    dictionary_file = "../data/..."
    t = Translator()

    corpus = loadList(corpus_file)
    annotated = t.translate(corpus)
    postprocessed = t.translate(annotated)

    print postprocessed

if __name__ == '__main__':
    main()
