alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def letters_from_index(index):
    if index < 26:
        return alphabet[index]
    else:
        factor = index // 26
        remainder = index % 26
        return letters_from_index(factor - 1) + alphabet[remainder]


def index_from_letters(letters):
    order = len(letters)
    factors = [(alphabet.index(letter) + 1) * 26 ** (order - i - 1) for i, letter in
               zip(range(order), letters)]
    factors[-1] -= 1
    return sum(factors)
