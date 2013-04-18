# phrase pair coverage

import ppe

def compare(train_files, held_out_files):
    train_freqs = ppe.extract_phrase_pair_freqs(train_files[0],
                    train_files[1], train_files[2], train_files[3])
    held_out_freqs = ppe.extract_phrase_pair_freqs(held_out_files[0],
                    held_out_files[1], held_out_files[2], 
                    held_out_files[3])

def compare_phrase(test_phrase, phrase_table, max_concat, concat_num):
    if concat_num > max_concat:
        return False
    phrase_splits = split_phrase(test_phrase, concat_num)
    for ps in phrase_splits:
        match = True
        for split in ps:
            if split not in phrase_table:
                match = False
                break
        if match:
            return True
    return compare_phrase(test_phrase, phrase_table, max_concat, concat_num+1)
