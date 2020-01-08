import os
import random
import string


def random_text_file_generator(word_length_range: int, word_number_range: int, files_number: int, path: str):

    for i in range(files_number):
        file_name = path + "/test" + "-" + str(i) + ".txt"
        with open(file_name, "w") as file:
            rand_word_number = random.randint(0, word_number_range)
            for j in range(rand_word_number):
                if j % 50 == 0:
                    file.write("\n")
                rand_word_length = random.randint(1, word_length_range)
                word = word_generator(rand_word_length)
                file.write(word)
                file.write(" ")


def word_generator(length=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.ascii_uppercase
                                   + string.ascii_lowercase + string.digits + string.punctuation):

    return ''.join(random.choice(chars) for _ in range(length))


if __name__ == '__main__':
    word_length_range = int(input("Enter word length range:"))
    word_number_range = int(input("Enter number of words range:"))
    files_number = int(input("Enter number of files:"))
    path = str(input("Enter where you want to save the files: "))
    random_text_file_generator(word_length_range, word_number_range, files_number, path)
