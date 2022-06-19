def get_words(path = 'words.txt', guess = False):
    words = set()
    if not guess:
        path = 'official-words.txt'
    with open(path) as f:

            for line in (f.readlines()):
                words.add(line.rstrip())

    return words