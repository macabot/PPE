# phrase pair coverage

"""
By Michael Cabot (6047262) and Sander Nugteren (6042023)
"""

import ast
import argparse
import ppe
import sys
import itertools

def compare(train_table, held_out_file, max_concat):
    """ Explore the coverage (sparsity) of the phrase table by computing 
    the percentage phrase pairs in a held-out set which:
    (a) are available in the training set phrase table, or
    (b) can be built by concatenating (in any order) n > 0 phrase pairs from
        the training set phrase table: it is important to set an upper-bound
        on n, E.g., n <= 3 which makes this more reasonable to execute
    
    Keywords arguments:
    train_table -- table of phrase pairs from training data
    held_out_file -- file name of file containing phrase pairs with their 
                     corresponding joint and conditional probabilities
    max_concat -- maximum number of concatenations. If max_concat==0, then
                  then whole phrase pair in the held out set must be present
                  in the train table
    
    Returns coverage of phrase pairs in the held out set
    """
    held_out_table = read_phrase_table_gen(held_out_file)
    correct = 0
    incorrect = 0
    num_lines = ppe.number_of_lines(held_out_file)
    for i, phrase_pair in enumerate(held_out_table):
        if i % (num_lines/100) is 0:
            sys.stdout.write('\r%d%%' % (i*100/num_lines,))
            sys.stdout.flush()

        if construct_phrase_pair(phrase_pair, train_table, max_concat):
            correct += 1
        else:
            incorrect += 1

    sys.stdout.write('\n')
    return correct/float(correct+incorrect)

def construct_phrase_pair(phrase, phrase_table, max_concat, concat_num = 0):
    """Build phrase pairs by splitting the phrases for each language and check
    if all the phrase pairs in one of the possible alignments between these splits 
    are present in the phrase table
    
    Keywords arguments:
    phrase -- a phrase pair
    phrase table -- set of phrase pairs
    max_concat -- maximum number of concatenations
    concat_num -- current number of concatenation (default is 0)
    
    Returns True if all sub phrase pairs are in the phrase table
    """
    if concat_num > max_concat:
        return False

    l1_phrase_splits = all_splits(concat_num, phrase[0])
    l2_phrase_splits = all_splits(concat_num, phrase[1])
    for l1_phrase, l2_phrase in itertools.product(l1_phrase_splits, l2_phrase_splits):
        for permutation in itertools.permutations(l2_phrase):
            match = True
            for i in xrange(concat_num+1):
                sub_phrase = (l1_phrase[i], permutation[i])
                if sub_phrase not in phrase_table:
                    match = False
                    break
        
            if match:
                return True

    return construct_phrase_pair(phrase, phrase_table, max_concat, concat_num+1)
    
def all_splits(splits, str):
    """Construct all possible splits of a phrase
    
    Keywords arguments:
    splits -- number of splits >= 0
    str -- contains words separated by spaces
    
    Returns a list of all possible splits where each element is a list of substrings
    """
    if splits == 0:
        return [[str]]

    split_words = []
    words = str.split()
    for i in xrange(1, len(words)):
        front = ' '.join(words[:i])
        back = ' '.join(words[i:])        
        tail = all_splits(splits-1, back)
        for t in tail:
            temp_split = [front]
            temp_split.extend(t)
            split_words.append(temp_split)

    return split_words

def read_phrase_table_gen(file_name):
    """Read phrase pairs from a file
    
    Keywords arguments:
    file_name -- name of file containing phrase table
    
    Yield phrase pair
    """
    file = open(file_name, 'r')
    for line in file:
        phrase_pair, _, _, _ = ast.literal_eval(line.strip())
        yield phrase_pair

    file.close()

def read_phrase_table(file_name):
    """Read phrase pairs from a file
    
    Keywords arguments:
    file_name -- name of file containing phrase table
    
    Set of all phrase pairs
    """
    print 'Reading %s ' % file_name
    file = open(file_name, 'r')
    phrase_table = set()
    num_lines = ppe.number_of_lines(file_name)
    i = 0
    for line in file:
        if i % (num_lines/100) is 0:
            sys.stdout.write('\r%d%%' % (i*100/num_lines,))
            sys.stdout.flush()

        phrase_pair, _, _, _ = ast.literal_eval(line.strip())
        phrase_table.add(phrase_pair)
        i += 1

    sys.stdout.write('\n')
    file.close()
    return phrase_table

def phrase_table_to_moses(file_name, out_name):
    """Read a phrase table and write it to a file using the moses format
    
    Keywords arguments:
    file_name -- name of file containing phrase table
    out_name -- name of file for writing phrase table in moses format
    """
    file = open(file_name, 'r')
    out = open(out_name, 'w')
    for line in file:
        phrase_pair, _, _, l2_given_l1 = ast.literal_eval(line.strip())
        l1, l2 = phrase_pair
        out.write('%s ||| %s ||| %s ||| |||\n' % (l1, l2, l2_given_l1))

    file.close()
    out.close()

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-t", "--trainfile",
        help="File containing phrases from the training set")
    arg_parser.add_argument("-v", "--heldoutfile",
        help="File containing phrases from the test set")
    arg_parser.add_argument("-m", "--max_concat",
        help="File containing phrases from the test set")
    args = arg_parser.parse_args()
    
    max_concat_list = [int(m) for m in args.max_concat.split(',')]
    
    print 'train file: %s' % args.trainfile
    print 'held-out file: %s' % args.heldoutfile
    print 'max concat list: %s' % max_concat_list
    
    train_table = read_phrase_table(args.trainfile)
    for max_concat in max_concat_list:
        coverage = compare(train_table, args.heldoutfile, max_concat)
        print 'max concat: %s' % max_concat
        print 'coverage: %s' % coverage
    