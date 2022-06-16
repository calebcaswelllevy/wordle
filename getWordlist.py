def get_words(path = 'words.txt'):
    words = set()
    with open(path) as f:

            for line in (f.readlines()):
                words.add(line.rstrip())

    return words