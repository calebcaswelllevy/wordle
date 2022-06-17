
import random
from getWordlist import get_words
import letters

class GameBoard():
    def __init__(self):
        self.guess_number = 0
        self.target_word = random.choice(tuple(get_words()))
        self.letter_bank = letters.LetterBank()