# phrase pair coverage

import ast
import argparse
import ppe
import sys
import itertools

def compare(train_table, held_out_file, max_concat):    
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
    file = open(file_name, 'r')
    for line in file:
        phrase_pair, _, _, _ = ast.literal_eval(line.strip())
        yield phrase_pair

    file.close()

def read_phrase_table(file_name):
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
    