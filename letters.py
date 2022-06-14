class LetterBank:
    def __init__(self):
        self.letters = 'abcdefghijklmnopqrstuvwxyz'.split()
        self.letter_status = {letter : "black" for letter in self.letters}

    def set_letter_status(self, letter, status):
        self.letter_status[letter] = status

    def get_letter_status(self, letter):
        return self.letter_status[letter]