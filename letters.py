class LetterBank:
    def __init__(self, target):
        self.target = target
        self.letters = 'abcdefghijklmnopqrstuvwxyz'
        self.letter_status = {letter : "black" for letter in self.letters}

    def __repr__(self):
        return self.letter_status

    def get_letters(self):
        return self.letters

    def set_letter_status(self, letter, status):
        self.letter_status[letter] = status

    def get_letter_status(self, letter):

        return self.letter_status[letter]


    def reset(self, target):
        self.letter_status = {letter : "white" for letter in self.letters}
        self.target = target

    def update_letter_status(self, word):
        '''
        method to update letter status dictionary given
        :param word: string word entered from user input
        :return: None
        '''
        for letter1, letter2 in zip(word, self.target):
            if letter1 == letter2:
                self.letter_status[letter1] = 'green'
            elif letter1 in self.target:
                self.letter_status[letter1] = 'yellow'
            else:
                self.letter_status[letter1] = 'gray'

    def change_letter_status_based_on_guess(self, new_letter_information:dict) -> None:
        '''
        method that takes a dict with letter status info and manually updates letter status for those letters.
        This method is for when the target is unkown.

        :param new_letter_information:  Dict with letters keys and status values from a guess
        :return: None
        '''
        for letter, status in new_letter_information.items():
            self.letter_status[letter] = status