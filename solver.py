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
        for letter in  self.letters_in_word:
            if not letter in word:
                return False
        return True

    def compute_letter_distribution_at_locus(self, index: int, word_choices:list) -> dict:
        #TODO: this will compute the distribution of letters at a locus
        count_dict = {letter: 0 for letter in self.letter_bank.letters}
        n = len(word_choices) + 1
        for word in word_choices:
            count_dict[word[index]] += 1
        prob_dict = {key : val / n for key, val in count_dict.items()}
        return prob_dict

    def get_letter_distributions(self, word_choices:list) -> list:
        #TODO: this will use compute_letter_distributions to calculate
        #TODO the prob of each letter at each locus
        return [self.compute_letter_distribution_at_locus(index, word_choices) for index in range(5)]

    def compute_word_entropy(self, word):
        count_dict = {letter : 0.1 for letter in word}

        for letter in word:
            if letter not in self.guessed_words:
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
        entropy = self.compute_word_entropy(word)
        word_value = self.compute_word_value(word, letter_distribution)
        #scale the variables
        entropy /= np.e
        entropy *= 3-iteration
        if iteration >= 2:
            return word_value
        #otherwise, return combined metric
        word_value /= 1.5

        total_value = entropy + word_value
        return total_value



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
        s = Solver(word)
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
            num_tries.append(n)
    print(f'Record: {sum(record)/len(record)}')
    print(f'Number tries = {sum(num_tries)/len(num_tries)}')
    return failed_words


def solve(word):
    s = Solver(word)
    best_word = ''
    # s.letter_bank.update_letter_status(best_word)
    n = 0
    while best_word != s.target:
        if n == 6:
            print(f'failed on {s.target}')
            break
        candidates = s.find_candidates(s.valid_words)
        let_dis = s.get_letter_distributions(candidates)
        best_word = s.find_best_word(let_dis, candidates, n)
        print(f'best_word at iteration {n} = {best_word}')

        s.letter_bank.update_letter_status(best_word)
        s.update_known_letters(best_word, s.target)
        print(f'known letters: {s.known_letters}')
        s.update_letters_not_at_locus(best_word, s.target)
        s.update_guessed_words(best_word)
        n += 1

#solve('lucky')
failures = test()
[ solve(failure) for failure in failures]
