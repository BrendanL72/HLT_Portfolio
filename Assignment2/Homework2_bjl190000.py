import sys
import os
import random

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

#  preprocesses raw text to get only the tokens and nouns of a passage
#  the tokens returned is a set of >5 characters long, lowercased, and alphatized tokens
def preprocess_text(raw_text):
   #tokenize and lowercase raw text
   tokens = [token.lower() for token in raw_text.split()]

   #filter out non alphanumeric and short tokens
   reduced_token_list = []
   for t in tokens:
      if len(t) > 5 and t.isalpha():
         if t not in stopwords.words('english'):
            reduced_token_list.append(t)

   #get only uniques lemma of the tokens
   wnl = WordNetLemmatizer()
   lemmas = [wnl.lemmatize(t) for t in reduced_token_list]
   lemma_set = set(lemmas)

   #get pos tags
   pos_lemmas = nltk.pos_tag(lemma_set)
   
   #create list of only nouns
   nouns = [l[0] for l in pos_lemmas if l[1] == "NN"]

   #print stats
   print("Number of tokens:", len(reduced_token_list))
   print("Number of nouns:", len(nouns))

   return (reduced_token_list, nouns)


#  guessing_game takes a list of words and plays a word guessing game similar to Hangman with the user in the command line
#  The game ends when the player's score is negative or the player's guess is '!'
#  Player score starts at 5 and increases by 1 for every correct guess regardless of the number of letters matching with the guessed letter
def guessing_game(word_list):
   score = 5

   print("Let's play a word guessing game!")
   # Keep giving the user words until he runs out of points
   while (score >= 0):
      # Select a new word
      new_word = random.choice(word_list)
      display_word = "_ " * len(new_word)
      guess_history = []

      # Guessing the word 
      while (score >= 0):
         print("")
         print(display_word)

         #Check if user has won the game
         current_word_progress = "".join(display_word.split())
         if (current_word_progress == new_word):
            print("Great job! You've solved it!")
            break

         guess = ".."
         #get the next guess letter
         while len(guess) != 1 and guess not in guess_history:
            guess = input("Guess a letter:")
            if guess != 1:
               print("Please input a character.")

         #exit the game
         if guess == "!":
            print("Game aborted.")
            return score

         #check if guess is in the word
         if (guess in new_word):
            for idx, ch in enumerate(new_word):
               if (ch == guess):
                  display_word = display_word[:2*idx] + ch + display_word[2*idx+1:]
                  
            score = score + 1
            print("Correct! Score is %s" % (score))
         else:
            score = score - 1
            if score < 0:
               print("Sorry, incorrect answer")
               break
            else:
               print("Sorry, guess again. Score is %s" % (score))

         guess_history.append(guess)
         print("Guesses so far:", " ".join(guess_history))
   
   #user lost
   if (score < 0):
      print("Game over! Better luck next time!")


if __name__ == "__main__":
   #getting the input file name
   args_list = sys.argv
   if len(args_list) <= 1:
      print("Error, no input file specified")
      sys.exit(1)
   input_file_name = args_list[1]
   input_file_path = os.path.relpath(input_file_name)
   print("Processing file:", input_file_path)

   #reading the input file
   file_handle = open(input_file_path, 'r')
   raw_text = file_handle.read()

   #find lexical diversity of the passage
   tokens = [token.lower() for token in raw_text.split()]
   unique_tokens = set(tokens)
   print("Num. tokens in text:", len(tokens))
   print("Num. unique tokens in text:", len(unique_tokens))

   lex_div = len(unique_tokens)/len(tokens)
   print("Lexical Diversity: %.2f" % (lex_div))

   #preprocess the raw text
   reduced_tokens, nouns = preprocess_text(raw_text)

   #find the top 50 words
   wnl = WordNetLemmatizer()
   lemmas = [wnl.lemmatize(t) for t in reduced_tokens]
   lemma_set = set(lemmas)
   noun_counts = {n:lemmas.count(n) for n in nouns}
   most_common_nouns = sorted(noun_counts.items(), key=lambda x: x[1], reverse=True)
   print(most_common_nouns[:5])

   #play a guessing game based on the top 50
   top_words_list = [n[0] for n in most_common_nouns][:50]
   guessing_game(top_words_list)