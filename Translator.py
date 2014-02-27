#-*- coding: utf-8 -*-

import sys
import os
import re
import sys
import nltk
import en

class Translator:
    def __init__(self):
        self.dictionary = {}
        self.preprocessed = []
        self.translated = []
        self.postprocessed = []
        brown_a = nltk.corpus.brown.tagged_sents()
        self.unigram_tagger = nltk.UnigramTagger(brown_a)

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

                    # Omit insignificant counting units
                    elif token_word == '\xea\xb0\x9c' and token_pos == 'NNB':
                        pass;

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


        for line in f:
            line = line.strip()
            entries = line.split(':')
            #print entries

            word = entries[0]
            
            if len(entries) > 1 and len(entries[1]) > 1:
                meanings = entries[1].split(',')
                annotated_meanings = self.unigram_tagger.tag(meanings)

                #print annotated_meanings I COMMENTED THIS OUT
                if word in self.dictionary:
                    self.dictionary[word] = annotated_meanings
                #else:
                #    print str(unicode(word)) # for debugging
                

    ### TO DO: CHOOSE THE RIGHT TRANSLATION AMONG MANY
    def translate(self):
        for sentence in self.preprocessed:
            translated_sentence = []
            prev_token = ()
            for token in sentence:
                korean_word = token[0]
                korean_pos = token[1]

                # Directly paste punctuation, numbers, foreign characters, etc.
                if korean_pos in ["SF", "SP", "SS", "SE", "SO", "SL", "SW", "SN"]:
                    translated_sentence.append(korean_word)

                # Tag plural suffix to previous word
                elif korean_pos == 'XSN' and korean_word == '\xeb\x93\xa4':
                    translated_sentence[-1] = translated_sentence[-1] + '<PLURAL>'

                elif korean_pos == 'NNB' and korean_word == '\xec\x88\x98':
                    translated_sentence.append("can")

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

                elif korean_pos == 'ETM' and prev_token == '\xea\xb0\x99':
                    translated_sentence[-1] = "like"

                # skip parts of speech (Korean endings) that do not have English counterparts
                elif korean_pos[0] == 'E':
                    if korean_word == '\xec\x97\x88':
                        translated_sentence.append('<PAST>')
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

                prev_token = (korean_word, korean_pos)
            self.translated.append(translated_sentence)

    def reorder(self, sentence):
        i = 0
        object_start = 0
        wasVerb = False
        while i < len(sentence):
            word = sentence[i]
            if word.endswith('<SUBJECT>'):
                wasVerb = False
                if i + 1 < len(sentence):
                    object_start = i + 1
            elif word.endswith('<OBJECT>'):
                object_start = i
                wasVerb = False
            elif word.endswith('<VERB>') and i != object_start:
                verb = sentence.pop(i);
                sentence.insert(object_start, verb)
                wasVerb = True
            elif wasVerb:
                object_start = i
                #insert a comma
                wasVerb = False
            i = i + 1

    def resolvePossessive(self, sentence):
        i = 0
        while  i < len(sentence):
            word = sentence[i]
            if word.endswith('<POSSESSIVE>'):
                splitWordPos = i
                splitWord = word.split('<')
                resolvedWord = possessiveForm(splitWord[0])
                i += 1
                while  i < len(sentence):
                    tagged = self.unigram_tagger.tag([sentence[i]])
                    if tagged[0][1] == 'NN' or sentence[i].endswith('<OBJECT>') or sentence[i].endswith('<SUBJECT>'):
                        sentence[i] = resolvedWord + ' ' + sentence[i]
                        sentence.pop(splitWordPos)
                        i -= 1
                        break
                    i += 1
            i += 1

    def resolvePlural(self, sentence):
      for i in range(len(sentence)):
          word = sentence[i]
          if '<PLURAL>' in word:
              pluralized = en.noun.plural(word[:word.find('<')])
              word = word.replace(word[:word.find('<')], "") # Remove word
              remainingTags = word.replace('<PLURAL>', "") # Remove plural tag
              sentence[i] = pluralized + remainingTags

          # Convert nearest noun to "few", "many", "several" or number to plural
          if word in ["few", "many", "several"] or (word.isdigit() and word != '1'):
            print word
            j = i + 1
            while j < len(sentence):
                next = sentence[j]
                if '<NOUN>' in next and '<PLURAL>' not in next:
                    pluralized = en.noun.plural(next[:next.find('<')])
                    next = next.replace(next[:next.find('<')], "") # Remove word
                    sentence[j] = pluralized + next
                    break
                j += 1


    # Find nearest verb and convert to past tense
    def resolvePastTense(self, sentence):
        i = 0
        while i < len(sentence):
            if sentence[i] == '<PAST>':
                j = i-1
                while j > 0:
                    prev_token = sentence[j]
                    if '<VERB>' in prev_token:
                        past_tense = en.verb.past(prev_token[:prev_token.find('<')])
                        prev_token = prev_token.replace(prev_token[:prev_token.find('<')], "") # Remove word
                        sentence[j] = past_tense + prev_token
                        sentence.pop(i)
                        break
                    j -= 1
            i += 1

    def combineNouns(self,sentence):
        wasNoun = False
        i = 0
        while i < len(sentence):
            word = sentence[i]
            tagged = ""
            if '<' in word:
                splitWord = word.split('<')
                tagged = '<' + splitWord[1]
                word = splitWord[0]
            annotated = self.unigram_tagger.tag([word])
            if annotated[0][1] == 'NN' or tagged == '<OBJECT>' or tagged == '<SUBJECT>':
                if wasNoun:
                    sentence[i] = sentence[i - 1] + ' ' + word + tagged
                    sentence.pop(i - 1)
                    if tagged == '<OBJECT>' or tagged == '<SUBJECT>':
                        wasNoun = False
                else:
                    if tagged == "":
                        wasNoun = True
                    i += 1

            else:
                wasNoun = False
                i += 1

    def breakup(self,sentence):
        i = 0
        while i < len(sentence):
            token = sentence[i]
            tokens = token.split()
            if len(tokens) > 1:
                sentence = sentence[:i] + tokens + sentence[i+1:]
            i += len(tokens)
        return sentence


    def tagVerbAndNoun(self,sentence):
        for i in xrange(len(sentence)):
            token = sentence[i]
            tag = self.unigram_tagger.tag([token])
            if tag[0][1] == 'VB' or tag[0][1] == 'BE':
                sentence[i] = token + '<VERB>'
            if tag[0][1] == 'NN':
                sentence[i] = token + '<NOUN>'

    
    ### TO DO: PREPROCESS TRANSLATED SENTENCES (correct grammar, reorder)
    def postprocess(self):
        for sentence in self.translated:
            sentence = self.breakup(sentence)
            self.tagVerbAndNoun(sentence)
            self.resolvePlural(sentence)
            self.resolvePossessive(sentence)
            self.combineNouns(sentence)
            self.reorder(sentence)
            self.resolvePastTense(sentence)

            sentence[0] = sentence[0].capitalize()

            self.postprocessed.append(sentence)
            printSentences(sentence)

possessiveSpecialCases = {
    'I':'my',
    'she':'her',
    'he':'his',
    'you':'your',
    'them':'their',
    'we':'our',
    'it':'its',
    'your':'yours',
    'our':'ours',
    'her':'hers',
    'their':'theirs',
    'who':'whose'
}

def possessiveForm(word):
    pf = possessiveSpecialCases.get(word)
    if pf:
        return pf
    if word.endswith('s'):
        return word + '\''
    else:
        return word + '\'s'


def loadList(file_name):
    """Loads corpus as lists of lines. """
    with open(file_name) as f:
        l = [line.strip() for line in f]
    return l

def printSentences(sentences):
    print ' '.join(sentences)
    #print sentences

def main():
    tokenized_file = "./data/dev-tokenized.txt"
    dictionary_file = "./data/dict.txt"

    t = Translator()
    t.preprocess(tokenized_file)

    t.importDictionary(dictionary_file)
    t.translate()
    t.postprocess()


    test_tokenized = "./data/test-tokenized.txt"
    dictionary_test = "./data/dict2.txt"
    t2 = Translator()
    t2.preprocess(test_tokenized)

    t2.importDictionary(dictionary_test)
    t2.translate()
    t2.postprocess()

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    print["수"]
    main()
