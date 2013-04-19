# phrase pair coverage

import ppe
import ast

def compare(train_files, held_out_files):
    train_freqs = ppe.extract_phrase_pair_freqs(train_files[0],
                    train_files[1], train_files[2], train_files[3])
    held_out_freqs = ppe.extract_phrase_pair_freqs(held_out_files[0],
                    held_out_files[1], held_out_files[2], 
                    held_out_files[3])

def compare_phrase(test_phrase, phrase_table, max_concat, concat_num):
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
    pass
    #phrae_table = read_phrase_table('../phrase-pairs/output.heldout.txt')
    #print phrase_table
