# phrase pair coverage

import ast

def compare(train_file, held_out_file, max_concat):
    train_table = read_phrase_table(train_file)
    held_out_table = read_phrase_table(held_out_file)
    correct = 0
    incorrect = 0
    for phrase_pair in held_out_table:
        if compare_phrase(phrase_pair, train_table, max_concat):
            correct += 1
        else:
            incorrect += 1
    return correct/float(correct+incorrect)

def compare_phrase(test_phrase, phrase_table, max_concat, concat_num=0):
    if concat_num > max_concat:
        return False
    phrase_splits = all_splits(concat_num, test_phrase)
    for ps in phrase_splits:
        match = True
        for split in ps:
            if split not in phrase_table:
                match = False
                break
        if match:
            return True
    return compare_phrase(test_phrase, phrase_table, max_concat, concat_num+1)
    
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

def read_phrase_table(file_name):
    file = open(file_name, 'r')
    phrase_table = []
    for line in file:
        phrase_pair, _, _, _ = ast.literal_eval(line.strip())
        phrase_table.append(phrase_pair)

    file.close()
    return phrase_table
    

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-trf", "--trainfile",
        help="File containing phrases from the training set")
    arg_parser.add_argument("-tstf", "--testfile",
        help="File containing phrases from the test set")
    arg_parser.add_argument("-mc", "--max_concat",
        help="File containing phrases from the test set")
    args = arg_parser.parse_args()
    print compare(args.trainfile, args.testfile, args.max_concat)
    #phrae_table = read_phrase_table('../phrase-pairs/output.heldout.txt')
    #print phrase_table
