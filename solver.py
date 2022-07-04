import random

import letters
from getWordlist import get_words
import numpy as np

class Solver:
    def __init__(self, target, letter_bank = None):
        self.target = target
        self.valid_words = get_words(guess=False)
        if not letter_bank:
            self.letter_bank = letters.LetterBank(target)
        else:
            self.letter_bank = letter_bank
        self.guessed_words = ''
        self.possible_choices = []
        self.known_letters = ['']*5
        self.letters_not_at_locus = [[],[],[],[],[]]
        self.letters_in_word = set()


    def find_candidates(self, word_choices:list) -> list:
        #TODO: this will use evaluate_match status to filter words
        return [word for word in word_choices if self.is_match(word)]

    def is_match(self, word:str) -> bool:
        #TODO: this will return whether a word fits criteria
        for index, letter in enumerate(word):
            #check if letter not in word:
            if self.letter_bank.get_letter_status(letter) == 'gray':
                return False
            #check if letter not at that index
            if self.known_letters[index] and letter != self.known_letters[index]:
                return False
            #check if a letter is known not to be at a locus
            if self.letters_not_at_locus[index] and letter in self.letters_not_at_locus[index]:
                return False
        #check if a letter known to be in the word is missing
        ''' for letter in  self.letters_in_word:
            if not letter in word:
                return False'''
        return True

    def compute_letter_distribution_at_locus(self, index: int, word_choices:list) -> dict:
        #TODO: this will compute the distribution of letters at a locus
        count_dict = {letter: 0 for letter in self.letter_bank.letters}
        n = len(word_choices) + 1
        for word in word_choices:
            try:
                count_dict[word[index]] += 1
            except:
                print(f'count dict = {count_dict}')
                print(f'word = {count_dict[word]}')
                print(f'index = {index}')
        prob_dict = {key : val / n for key, val in count_dict.items()}
        return prob_dict

    def get_letter_distributions(self, word_choices:list) -> list:
        #TODO: this will use compute_letter_distributions to calculate
        #TODO the prob of each letter at each locus
        return [self.compute_letter_distribution_at_locus(index, word_choices) for index in range(5)]

    def compute_word_entropy(self, word):
        count_dict = {letter : 0.1 for letter in word}

        for letter in word:
            if not letter in self.guessed_words:
                count_dict[letter] += 1
        freq_dict = {letter : count / 5 for letter, count in count_dict.items()}
        shannon_dict = {letter : np.log(p) * p for letter, p in freq_dict.items()}

        shannon_h = sum(shannon_dict.values())
        return -shannon_h

    def find_highest_entropy_word(self, wordlist):
        best_h = -1
        best_word = ''
        for word in wordlist:
            h = self.compute_word_entropy(word)
            if h > best_h:
                best_h, best_word = h, word
        return best_word

    def compute_word_value(self, word, letter_distributions):
        #TODO: this will compute the value of a word given letter distributions
        prob_letters_in_right_spot = sum( [letter_distributions[index][letter] for index, letter in enumerate(word) ])
        #prob letter is somewhere else:
        prob_letters_elsewhere = 0
        for index1, letter in enumerate(word):
            prob_letter_elsewhere = 0
            for index2 in range(5):
                if index1 != index2:
                    prob_letter_elsewhere += letter_distributions[index2][letter]
            prob_letters_elsewhere += prob_letter_elsewhere

        word_value = prob_letters_in_right_spot + (0.5 * prob_letters_elsewhere)
        return word_value

    def explore_exploit(self, word, iteration, letter_distribution):
        #calculate the metrics
        n_letters = 0
        for letter in self.known_letters:
            if not not letter:
                n_letters += 1
        entropy = self.compute_word_entropy(word)
        word_value = self.compute_word_value(word, letter_distribution)
        #scale the variables
        entropy /= np.e
        entropy *= 4 - iteration

        #if we are in the endgame, return raw value:
        if iteration > 1 and n_letters-iteration > 1:
            return word_value
        #otherwise, return combined metric
        word_value /= 1.5

        total_value = entropy + word_value
        return total_value

    def find_wildcard_letters(self, candidates:list) -> list:
        '''
        This finds shared letters, and if there is a wildcard locus it finds the letters to test.
        A wildcard situation is when four letters are shared among candidate words, and one index is highly variable.
        This situation needs a separate algorithm to handle properly because guessing any one of the candidate words will only eliminate
        one word from the candidate pool. By guessing a word containing all wildcard letters that is not in the candidate pool,
        we can gain information about all letters in one guess.

        PARAMS:
        :candidates: list of candidate words to search for similar letters

        RETURNS:
        a list of wildcard letters.
        '''
        shared_letters = []
        wildcard_letters = set()
        n_words = len(candidates)
        for index in range(5):
            counts = {}
            for word in candidates:
                letter = word[index]
                if not letter in counts:
                    counts[letter] = 1
                else:
                    counts[letter] += 1
            for letter, count in counts.items():
                #if word is more than 90% prevalent, it is a shared word
                if count / n_words > 0.9:
                    shared_letters.append(letter)
                #if a word occurs 2 times or less at this index, it is a wildcard:
                elif count <= 2:
                    wildcard_letters.add(letter)
        #check if this is a wildcard situation:
        if len(shared_letters) == 4:
            return wildcard_letters
        else:
            return []

    def deal_with_wildcards_in_endgame(self, letter_set):
        '''
        This is a wrapper function that implements an algorithm to handle wildcard situations

        A wildcard situation is when four letters are shared among candidate words, and one index is highly variable.
        This situation needs a separate algorithm to handle properly because guessing any one of the candidate words will only eliminate
        one word from the candidate pool. By guessing a word containing all wildcard letters that is not in the candidate pool,
        we can gain information about all letters in one guess.

        The algorithm works as follows: 1) test if it is a wildcard situation by counting (semi)-unanimous letters, and if so find the wildcard
        letters that occupy the variable index position of the candidate words. 2) looking at all guessable words, find the set of words with the highest
        number of wildcard letters (max = number of candidate words). 3) return this list. This will form the list of candidate words for the normal word
        selection routine.

        :param letter_set:
        :return:
        '''
        n_letters = len(letter_set)
        word_bank = get_words(guess = True)
        count_groups = self.find_words_with_letters(word_bank, letter_set)
        words_to_use = count_groups[n_letters]
        #if no words have all the letters, go down until there is at least one word to choose:
        while len(words_to_use) < 1:
            n_letters -=1
            words_to_use += count_groups[n_letters]
        return words_to_use

    def find_words_with_letters(self, word_bank, letter_set):
        #TODO: filters a set of words to subset containing most of letter set

        #initialize hash table to hold list of words with letter counts
        count_groups = {count : [] for count in len(letter_set)}
        # count letters in word, and put into appropriate bucket:
        for word in word_bank:
            count = self.word_contains_letters(word, letter_set)
            count_groups[count].append(word)

        return count_groups

    def word_contains_letters(self, word, letter_set):
        #TODO: returns number of letters contained by word:
        count = []
        for letter in letter_set:
            if letter in word:
                count += 1
        return count




    def find_best_word(self, letter_distributions, word_choices, iteration):
        # this will return a word from the word choices that maximizes value function
        best_word = ''
        best_value = -1
        for word in word_choices:
            current_value = self.explore_exploit(word, iteration, letter_distributions)
            if current_value > best_value:
                best_word, best_value = word, current_value

        return best_word

    def update_known_letters(self, guess, target):
        for index, (letter1, letter2) in enumerate(zip(guess, target)):
            if letter1 == letter2:
                self.known_letters[index] = letter1

    def update_letters_not_at_locus(self, guess, target):
        for index, (letter1, letter2) in enumerate(zip(guess, target)):
            if letter1 != letter2:
                self.letters_not_at_locus[index].append(letter1)
    def update_letters_in_word(self, guess):
        for letter in guess:
            if self.letter_bank.get_letter_status(letter) == 'yellow' and not letter in self.letters_in_word:
                self.letters_in_word.add(letter)
    def update_guessed_words(self, word):
        self.guessed_words += word

    def update_knowledge(self, guess, target):
        self.letter_bank.update_letter_status(guess)
        self.update_known_letters(guess, target)
        self.update_letters_not_at_locus(guess, target)
        self.update_letters_in_word(guess)
        self.update_guessed_words(guess)


class Hinter(Solver):
    def __init__(self, target = None):
        pass
    def enter_guess(self, word:str, letter_status: dict) -> None:
        # update guessed words
        self.guessed_words += word

        # update letter bank
        for index, (letter, status) in enumerate(letter_status.items()):
            self.letter_bank.set_letter_status(letter, status)

            #update known letters:
            if status == "green":
                self.known_letters[index] = letter
            elif status == "yellow":
                self.letters_not_at_locus[index] = letter

    def hint(self, n):
        candidates = self.find_candidates(self.valid_words)
        let_dis = self.get_letter_distributions(candidates)
        best_word = self.find_best_word(let_dis, candidates, n)
        return best_word






def test():
    record = []
    num_tries = []
    failed_words = []
    for word in get_words(guess = False):
        (win, tries) = solve(word)
        record.append(win)
        if not win:
            failed_words.append(word)
        if tries:
            num_tries.append(tries)
        '''s = Solver(word)
        best_word = ''
        #s.letter_bank.update_letter_status(best_word)
        n = 0
        while best_word != s.target:
            if n == 6:
                record.append(0)
                #print(f'failed on {s.target}')
                failed_words.append(s.target)
                break
            candidates = s.find_candidates(s.valid_words)
            let_dis = s.get_letter_distributions(candidates)
            #print(let_dis)
            best_word = s.find_best_word(let_dis, candidates, n)
           # print(f'best_word at iteration {n} = {best_word}')
            s.letter_bank.update_letter_status(best_word)
            s.update_known_letters(best_word, s.target)
            s.update_letters_not_at_locus(best_word, s.target)
            s.update_guessed_words(best_word)
            n += 1
        else:
            record.append(1)
            num_tries.append(n)'''

    print(f'Record: {sum(record)/len(record)}')
    print(f'Number tries = {sum(num_tries)/len(num_tries)}')
    return failed_words


def solve(word, verbose=False):
    s = Solver(word)
    best_word = ''
    # s.letter_bank.update_letter_status(best_word)
    n = 0
    while best_word != s.target:
        if n == 6:
            if verbose:
                print(f'failed on {s.target}')
            return (0, None)
        wildcard_candidates = []
        if n == 3 or n == 4: #test for a wildcard situation in the endgame
            wildcard_candidates = s.find_wildcard_letters(candidates)
        if wildcard_candidates:
            candidates = wildcard_candidates
        else:
            candidates = s.find_candidates(s.valid_words)

        let_dis = s.get_letter_distributions(candidates)
        best_word = s.find_best_word(let_dis, candidates, n)
        if verbose:
            if n > 0:
                print(f'candidates = {candidates}')
            print(f'best_word at iteration {n} = {best_word}')

        s.update_knowledge(best_word, s.target)
        n += 1
    return (1, n)


if __name__ == '__main__':

    #solve('lucky')
    failures = test()

    [ solve(failure, verbose=True) for failure in failures]
    print('failed words:')
    print(failures)