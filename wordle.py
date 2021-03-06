# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import random
import sys
import checkWord
from tkinter import *
from tkinter import ttk
from getWordlist import get_words
import numpy as np
from functools import partial
import json
from letters import LetterBank
import solver

guess_number = 0
target_word = ''
letter_bank = LetterBank('target_word')

def start_up():
    """

    :return:
    """
    try:
        user = sys.argv[1].lower()
    except:
        print("Warning: no username entered, user defaulting to 'Madison'")
        print("Example Usage: '$ python3 wordle.py Madison'")
        user = 'madison'
    try: #if a record exists, open it
        with open('record.json') as f:
            record = json.load(f)
    except: # no records exist, start new dict
        record = {
            user : {
                'record' : [1] ,
                'num_tries': [1]
            }

        }

    if not user in record:
        record[user] = {
            'record' : [1],
            'num_tries' : [1]
        }
    return user, record

def main():
    global target_word
    #global letter_bank
    user, record = start_up()

    # initialize frame:

    root = Tk()
    root.title("Wordle")
    root.geometry('725x770')
    frm = ttk.Frame(root, padding=0)
    frm.grid()

    placeholder = Canvas(frm, width = 50, height = 20)
    placeholder.grid(column=0, row=0)
    entry_box = Entry(frm, width = 29, borderwidth=5, font = ('Helvetica', 20))
    entry_box.grid(columnspan=3, column=1, row = 0, padx = 10, pady=10)
    canvas = Canvas(frm, width = 400, height = 470)
    canvas.grid(row = 3, column= 1, columnspan=3)

    message_holder = LabelFrame(root)
    message_holder.place(x=450, y = 100, width= 270, height = 150)
    message_box = Label(message_holder, font = ('Helvetica', 20))
    message_box.pack()
    message_box.config(text = f"{user.capitalize()}'s Wordle \n\n")
    record_display = Label(root, font = ('Helvetica', 20))
    record_display.place(x = 470, y = 330)

    average_tries_display = Label(root, font = ('Helvetica', 20))
    average_tries_display.place(x = 470, y = 360)

    # Letter holder:
    letter_holder = Canvas(root,
                           width="550",
                           height="170")
    letter_holder.place(x=20, y=580)
    letter_holder.config(background='gray')

    def render_letter_bank(new_word, letter_bank, canvas):
        #update letter bank:
        letter_bank.update_letter_status(new_word)
        #generate coordinates
        x_locations_top_and_middle = list(np.linspace(10, 500, 9))*2
        x_locations_bottom = list(np.linspace(25, 475, 8))
        x_locations = x_locations_top_and_middle + x_locations_bottom
        y_locations = list(np.linspace(10, 125, 3))
        y_locations = [y_locations[0]] * 9 + [y_locations[1]] * 9 + [y_locations[2]] * 8



        #draw the letters
        letter_boxes = {}
        for letter, x, y in zip(letter_bank.get_letters(), x_locations, y_locations):

            letter_boxes[letter] = canvas.create_rectangle( x, y,
                                                            x + 45, y + 45,
                                                            fill=letter_bank.get_letter_status(letter),
                                                            outline='white')
            canvas.create_text(x+23, y+25, text=letter.upper(), font=('Helvetica', 36), fill='black')


    def draw_board():
        x_locations = np.arange(0, 321, 80)
        y_locations = np.arange(0, 410, 80)
        rectangles = {}
        for x_start in x_locations:
            rectangles[x_start] = {}
            for y_start in y_locations:
                rectangles[x_start][y_start] = canvas.create_rectangle(x_start, y_start, x_start + 60, y_start + 60,
                                                                       fill='beige', outline='white')
        return rectangles

    def reset():

        global target_word
        target_word = random.choice(tuple(target_words))
        message_box.config(text=f"{user.capitalize()}'s Wordle \n\n")
        record_display.config(text=f"Win Percentage: {round(np.mean(record[user]['record']) * 100, 1)}")
        average_tries_display.config(text=f"   Average Tries:     {round(np.mean(record[user]['num_tries']), 1)}")

        # initialize guess number:
        global guess_number
        guess_number = 0

        rectangles = draw_board()
        # can.create_rectangle(20,20, 40, 40, fill = 'red', outline = 'blue')

        Button(frm, text='ENTER Word', command=enter_word_partial, height=1, width=13).grid(column=4, row=3)
        ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=4)
        ttk.Button(frm, text="Reset", command=reset).grid(column=2, row=4)

        #reset letterbank:
        try:
            letter_bank.reset(target=target_word)
        except:
            print(letter_bank)
        hinter = solver.Solver(target_word, letter_bank)
        render_letter_bank('    ', letter_bank, letter_holder)
    def enter_word(*args):

        global guess_number
        #print(f'guess nu ber: {guess_number}')
        word = entry_box.get().lower()
        entry_box.delete(0, END)

        if len(word) != 5:
            msg = 'word must be 5 letters long'
        elif not checkWord.check(word, valid_words):
            msg = 'Invalid Word, please try again'
        elif word == target_word:
            render_word( word, guess_number)
            render_letter_bank(word, letter_bank, letter_holder)
            msg = f'You Guessed It!!!\n' \
                  f' It was {target_word}'
            record[user]['record'].append(1)
            record[user]['num_tries'].append(guess_number + 1)
            with open('record.json', "w") as f:
                json.dump(record, f)
            record_display.config(text=f"Win Percentage: {round(np.mean(record[user]['record']) * 100, 1)}")
            average_tries_display.config(text=f"   Average Tries:     {round(np.mean(record[user]['num_tries']), 1)}")
        else:
            render_word( word, guess_number)
            render_letter_bank(word, letter_bank, letter_holder)
            if guess_number == 5:
                msg = f'Game Over!\n\nThe word was {target_word}'
                record[user]['record'].append(0)
                record[user]['num_tries'].append(5)
                with open('record.json', "w") as f:
                    json.dump(record, f)
                record_display.config(text=f"Win Percentage: {round(np.mean(record[user]['record']) * 100, 1)}")
                average_tries_display.config(text=f"   Average Tries:     {round(np.mean(record[user]['num_tries']), 1)}")
            else:
                msg = f'Try again.\n you have {4-guess_number} guesses left.'
            guess_number += 1



        message_box.config(text=f"{user}'s Wordle \n\n{msg}")

    enter_word_partial = partial(enter_word, guess_number)

    def render_word(word, guess_number):

        y_index = guess_number * 80
        #tally letters:

        for index, (x_start, letter) in enumerate(zip(locations, word)):
                #letter in right spot:
                if letter == target_word[index]:
                    #draw a green rectangle
                    canvas.create_rectangle(x_start, y_index, x_start + 60, y_index + 60, fill = 'green', outline = 'white')
                elif letter in target_word:
                    canvas.create_rectangle(x_start, y_index, x_start + 60, y_index + 60, fill='yellow', outline='white')

                canvas.create_text((x_start + 30, y_index + 37), text=letter, font = ('Helvetica', 40), fill = 'black')

    def get_colors(target_word:str, guess:str) ->list:
        '''
        TODO: returns a dict of indexes and colors
        :param target_word:
        :param guess:
        :return:
        '''
        #initialize count dict of unmatched letters in target word
        unmatched_letters = {}
        letter_colors = [None for index in target_word]
        if len(target_word) != len(guess):
            return letter_colors

        #loop through to find correct letters and count unmatched letters
        for index, (guess_letter, target_letter) in enumerate(zip(guess, target_word)):
            if guess_letter == target_letter:
                letter_colors[index] = 'green'
            else: #increment letter
                unmatched_letters[target_letter] = unmatched_letters.get(target_letter, 0) + 1

        #loop through to find letters in the wrong spot
        for index, (guess_letter, target_letter) in enumerate(zip(guess, target_word)):
            if guess_letter != target_letter:
                if unmatched_letters.get(guess_letter):
                    #letter in wrong spot, color yellow and decrement letter count
                    letter_colors[index] = 'yellow'
                    unmatched_letters[guess_letter] -= 1
                else:
                    #letter not in word color gray
                    letter_colors[index] = 'gray'

        return letter_colors


    #get the words

    valid_words = get_words(guess = True)
    target_words = get_words(guess = False)
    print(valid_words == target_words)

    target_word = random.choice(tuple(target_words))





    #draw board:

    locations = np.arange(0, 321, 80)
    rectangles = {}
    for x_start in locations:
        rectangles[x_start] = {}
        for y_start in locations:

           rectangles[x_start][y_start] = canvas.create_rectangle(x_start, y_start, x_start + 60, y_start + 60, fill = 'beige', outline = 'white')
    #can.create_rectangle(20,20, 40, 40, fill = 'red', outline = 'blue')
    reset()
    root.bind('<Return>', enter_word_partial)
    Button(frm, text='ENTER Word', command=enter_word_partial, height=1, width = 13).grid(column=4, row=3)
    ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=4)
    ttk.Button(frm, text="Reset", command=reset).grid(column=2, row=4)






    #ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
    root.mainloop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
