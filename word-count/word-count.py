import os
import shutil
import re
import random
import numpy as np
import matplotlib.pyplot as plt
from zipfile import ZipFile
import tarfile
from typing import List


def __count__(content: str) -> int:
    """
    This function counts how many words in a given string. A word can contain letters, numbers, ', - and can be an email
    with regex \b[A-Za-z0-9.]+@[A-Za-z0-9.]+\.[A-Za-z]{2,}. Any other punctuation separate words from each other.
    :param content: file path as string
    :return: number of words
    """
    content_list = __split_content__(content)  # Getting the words from string by splitting at white space, new line and
    # punctuation chars except '.-@.
    counter = 0  # initializing word counter
    for word in content_list:
        if word:
            emails = __email_match__(word)  # getting the emails from a word as a list.
            if emails:  # checking if the list is not empty
                # for _ in emails:
                #     counter = counter + 1
                counter = counter + len(emails)

                other_words = __remove_emails__(word)  # Removing the emails and getting anything else

                # clean_words_list = []
                for other_word in other_words:  # cleaning the rest of the words from . @ chars.
                    clean_words_list = __clean_words__(other_word)
                    counter = counter + len(clean_words_list)

                # for _ in clean_words_list:
                #     counter = counter + 1

            else:  # If the word does not contain emails, we will split  at . and @ if they exist.
                word_list = __clean_words__(word)  # cleaning the word from . @ chars.
                # for _ in word_list:
                #     counter = counter + 1
                counter = counter + len(word_list)

    return counter


def __email_match__(s: str) -> List[str]:
    """
    This function takes a string and return all the emails that match
    the following regex: r'\b[A-Za-z0-9.]+@[A-Za-z0-9.]+\.[A-Za-z]{2,}\b'.
    :param s: a string
    :return: list of all emails in s
    """
    result = re.findall(r'\b[A-Za-z0-9.]+@[A-Za-z0-9.]+\.[A-Za-z]{2,}\b', s)  # finds all emails that match the regex.
    return result


def __remove_emails__(s: str) -> List[str]:
    """
    This function takes a string and splits the string at every email and return list of non-email words. An email is
    defined by this regex: r'\b[A-Za-z0-9.]+@[A-Za-z0-9.]+\.[A-Za-z]{2,}\b.
    :param s: a string.
    :return: a list of all non-email words without empty and dash-only strings.
    """
    other_words = re.split(r'\b[A-Za-z0-9.]+@[A-Za-z0-9.]+\.[A-Za-z]{2,}\b', s)  # getting non-email words
    other_words = list(filter(None, other_words))
    # for other_word in other_words:  #TODO remove dashes
    #
    return other_words


def __split_content__(content: str) -> List[str]:
    """
    This function splits a string at punctuation chars except . ' - and @. And returns the words in a list.
    :param content: a string
    :return: list of strings
    """
    content_list = re.split(r'[`=~!#$%^&*()_+\[\]{};\\:"|<,/<>?\s]+', content)
    return content_list


def __count_file__(path: str) -> int:
    """
    This function opens a txt file given its path and returns its content as string.
    :param path: str
    :return: str
    """
    c = 0
    with open(path, 'r') as file:
        while True:
            line = file.readline()
            if not line:
                break
            c = c + __count__(line)

        return c


def __clean_words__(word: str) -> List[str]:
    """
    This function takes a word and splits it at . @ chars and return list of the split words.
    :param word: a string
    :return: list of strings
    """
    words = re.split(r'[@.]+', word)
    words = list(filter(None, words))  # Removing empty strings
    for word in words:
        if not re.findall(r'[0-9A-z]', word):  # Removing dash-only strings
            words.remove(word)
    return words


def __walk_zip__(path: str, counts: List[int]):
    """
    This function searches for txt files in zip file and counts how many words in each file and saves the result in
    count list. If it counters a zip file or tgz file, it will extract it temporally and and call __walk_zip__ or
    __walk_tgz__ recursively.
    :param path: str, zip file path
    :param counts: list
    :return: None
    """
    try:
        with ZipFile(path, 'r') as zip_ob:
            file_paths = zip_ob.namelist()
            for file_path in file_paths:
                if file_path.endswith(".txt"):
                    try:
                        with zip_ob.open(file_path) as file:
                            c = 0
                            while True:
                                line = file.readline().decode('utf-8')
                                if not line:
                                    break
                                c = c + __count__(line)
                            counts.append(c)
                    except:
                        print("Could not open " + path + "/" + file_path)
                elif file_path.endswith(".zip"):
                    try:
                        extract_path = __extract_file__(zip_ob, file_path, path)
                        file_path = extract_path + "/" + file_path
                        __walk_zip__(file_path, counts)
                        __remove_extracted_file__(extract_path)
                    except:
                        print("Could not extract " + path + "/" + file_path)
                elif file_path.endswith(".tgz"):
                    try:
                        extract_path = __extract_file__(zip_ob, file_path, path)
                        file_path = extract_path + "/" + file_path
                        __walk_tgz__(file_path, counts)
                        __remove_extracted_file__(extract_path)
                    except:
                        print("Could not extract " + path + "/" + file_path)
    except:
        print("Could not open " + path)


def __walk_tgz__(path: str, counts: List[int]):
    """
    This function searches for txt files in tgz file and counts how many words in each file and saves the result in
    count list. If it counters a zip file or tgz file, it will extract it temporally and and call __walk_zip__ or
    __walk_tgz__ recursively.
    :param path: str, tgz file path
    :param counts: list
    :return: None
    """
    try:
        tar_ob = tarfile.open(path)
        members = tar_ob.getmembers()
        for member in members:
            if member.name.endswith(".txt"):
                try:
                    extract_path = __extract_file__(tar_ob, member, path)
                    file_path = extract_path + "/" + member.name
                    c = __count_file__(file_path)
                    __remove_extracted_file__(extract_path)
                    counts.append(c)
                except:
                    print("Could not extract " + path + "/" + member.name)
            elif member.name.endswith(".zip"):
                try:
                    extract_path = __extract_file__(tar_ob, member, path)
                    file_path = extract_path + "/" + member.name
                    __walk_zip__(file_path, counts)
                    __remove_extracted_file__(extract_path)
                except:
                    print("Could not extract " + path + "/" + member.name)
            elif member.name.endswith(".tgz"):
                try:
                    extract_path = __extract_file__(tar_ob, member, path)
                    file_path = extract_path + "/" + member.name
                    __walk_tgz__(file_path, counts)
                    __remove_extracted_file__(extract_path)
                except:
                    print("Could not extract " + path + "/" + member.name)
    except:
        print("Could not open " + path)


def __walk_directory__(path: str, counts: List[int]):
    """
    This function searches for txt files in a directory and its children and counts how many words in each file and
    saves the result in  count list. If it encounters a zip file or tgz file, it will extract it temporally and and call
     __walk_zip__ or  __walk_tgz__ to search for txt files inside them.
    :param path: str, directory path
    :param counts: list
    :return: None
    """
    for (root, dirs, files) in os.walk(path, topdown=True):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                try:
                    c = __count_file__(file_path)
                    counts.append(c)
                except:
                    print("Could not open " + file_path)
            elif file.endswith(".zip"):
                file_path = os.path.join(root, file)
                __walk_zip__(file_path, counts)
            elif file.endswith(".tgz"):
                file_path = os.path.join(root, file)
                __walk_tgz__(file_path, counts)


def __extract_file__(ob, member, path: str) -> str:
    rand_int = random.randint(10000, 5000000)
    if path.endswith(".zip"):
        path = path.replace(".zip", "")
    elif path.endswith(".tgz"):
        path = path.replace(".tgz", "")
    extract_path = path + str(rand_int)
    ob.extract(member, extract_path)
    return extract_path


def __remove_extracted_file__(path: str):
    shutil.rmtree(path)


def __plot__(counts: List[int], save_path=""):
    """
    This function plots the count list and shows how many files have the same count range.
    :param counts:
    :param save_path:
    :return:
    """

    bins = int(len(counts) * 0.15) + 3  # take 15% of the number of files as number of bins

    plt.hist(counts, bins=bins, rwidth=0.95)
    plt.xlabel("Word Count")
    plt.ylabel("Number of files")
    plt.title("Word Count Histogram")
    if save_path:
        plt.savefig(save_path)
    plt.show()


def __path_word_counts__(path: str) -> List[int]:
    counts = []
    if path.endswith(".txt"):
        try:
            c = __count_file__(path)
            counts.append(c)
        except:
            print("Could not open " + path)
            return
    elif path.endswith(".zip"):
        __walk_zip__(path, counts)
    elif path.endswith(".tgz"):
        __walk_tgz__(path, counts)
    elif os.path.isdir(path):
        __walk_directory__(path, counts)
    else:
        print("The type of the path: " + path + " is not allowed.")

    return counts


def run():
    """
    Use this function to run the application.
    :return: None
    """
    path = input("Please enter a path: ")

    while not os.path.exists(path):
        print("Path: " + path + " does not exist")
        path = input("Please enter another path: ")

    counts = __path_word_counts__(path)
    if len(counts) == 0:
        print("No text file is found.")
    else:
        ans = input("Do you want to save the output? (y/n): ")
        while ans.lower() != "y" and ans.lower() != "n":
            ans = "Please enter y or n as the answer: "

        if ans.lower() == "n":
            __plot__(counts)
        else:
            save_path = input("Please enter where you want to save the output: ")
            __plot__(counts, save_path)


if __name__ == '__main__':
    run()
