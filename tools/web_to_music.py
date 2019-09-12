"""
This program gets the info from the online database and replaces the ID3 genre tags from the given database with the
online genres
"""

import sys

from tools.common import *



def process_collection(directory, language, purge):
    """
    Process the collection found under the given directory. All subdirectories are processed too.
    :param directory: Directory to process
    :param language:  Language to get the dance names in
    :param purge:     Clear the genre field if no dance data is found
    :return:
    """
    updated_data_list = []
    unknown_data_list = []
    missing_data_list = []
    for dirName, subdirList, fileList in os.walk(directory):
        for fname in fileList:
            track, found, dances_found = update_file(os.path.join(dirName, fname), language, purge)
            if found:
                if dances_found:
                    updated_data_list += [track]
                else:
                    unknown_data_list += [track]
            else:
                missing_data_list += [track]
    print("Found {:} matches with dance data, {:} without dance data, and {:} tracks were unknown to the database".format(len(updated_data_list), len(unknown_data_list), len(missing_data_list)))

def printUsage(argv):
    print("Usage: {:} <collection-path> <genre-language> [purge]".format(argv[0]))
    print("    In which <genre-language> is defined in the database")
    print("    Most likely supported: Nederlands, Dutch, Néerlandais")
    print("                           Français, French, Frans")
    print("                           English, Engels, Englais")

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        printUsage(sys.argv)
        exit(0)
    purge = len(sys.argv) > 3 and sys.argv[3] == "purge"
    process_collection(sys.argv[1], sys.argv[2], purge)