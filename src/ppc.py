# phrase pair coverage

import ppe

def compare(train_files, held_out_files):
    train_freqs = ppe.extract_phrase_pair_freqs(train_files[0],
                    train_files[1], train_files[2], train_files[3])
    held_out_freqs = ppe.extract_phrase_pair_freqs(held_out_files[0],
                    held_out_files[1], held_out_files[2], 
                    held_out_files[3])