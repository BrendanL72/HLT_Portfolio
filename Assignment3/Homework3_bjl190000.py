from nltk.corpus import wordnet as wn


if __name__ == "__main__":
   #noun
   noun = "fish"
   word_synsets = wn.synsets(noun)
   print("Synsets: \n", word_synsets)

   #get noun definition
   synset_sample = word_synsets[0]
   synset_sample_name = synset_sample.name()
   print(wn.synset(synset_sample_name).definition())

   #get hierarchical words
   print("Hypernyms:\n",synset_sample.hypernyms())
   print("Hyponyms:\n", synset_sample.hyponyms())
   print("Meronyms:\n",synset_sample.part_meronyms())
   print("Holonyms:\n", synset_sample.part_holonyms())
   print("Antonyms:\n", synset_sample.lemmas()[0].antonyms())


   #verb
   verb = "examine"
   verb_synsets = wn.synsets(verb)
   print(verb_synsets)

   #get verb information
   verb_synset_sample = verb_synsets[2]
   verb_synset_name = verb_synset_sample.name()
   print("Definition:\n", wn.synset(verb_synset_name).definition())
   print("Examples:\n", wn.synset(verb_synset_name).examples())
   print("Lemmas:\n", wn.synset(verb_synset_name).lemmas())

   #traverse up the synset hierarchy 
   print("Traversal:")
   while len(verb_synsets) > 1:
      print(verb_synsets)
      verb_synset_sample = verb_synsets[0]
      verb_synsets = wn.synsets(verb_synset_sample.name())

   print(verb_synset_sample)
   
   #show all forms of the verb
   print(wn.morphy("examining", wn.VERB))
   print(wn.morphy("examined"))

   #word similarity

   #sentiword net

   #collocation
