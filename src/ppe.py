# phrase pair extractor

import argparse

def extract_phrase_pair_freqs(alignments, language1, language2):
    phrase_pairs = []
    alignments = open(alignments, 'r')
    language1 = open(language1, 'r')
    language2 = open(language2, 'r')
    return phrase_pairs

def extract_alignments(word_alignments):
    phrase_alignment_list = []
    # First form words into phrase pairs
    while len(word_alignments):
        phrase_alignment = []
        phrase_alignment_init = word_alignments.pop()
        phrase_alignment_exp = [[phrase_alignment_init[0]], [phrase_alignment_init[1]]]
        while phrase_alignment_exp[0] or phrase_alignment_exp[1]:
            added_points = [(x,y) for (x,y) in word_alignments if (x in phrase_alignment_exp[0] or y in phrase_alignment_exp[1])]
            phrase_alignment.extend(added_points)
            word_alignments -= added_points
            phrase_alignment_exp = phrase_alignment_expansions(phrase_alignment)
        phrase_alignment_list.append(phrase_range(phrase_alignment))
    #Then loop over phrase pairs to join them together into new ones
    phrase_queue = list(phrase_alignment_list)
    while len(phrase_queue):
        p1 = phrase_queue.pop()
        new_p3 = []
        for p2 in phrase_queue:
            p3 = None
            #p2 above, to the left of p1
            #if p1[0:2] == p2[2:4]:
            #    p3 = p2[0], p2[1], p1[2], p1[3]
            #elif p1[2] == p2[0] and p1[3]
            if p3:
                new_p3.append(p3)
        phrase_alignment_list.append(new_p3)
        phrase_queue.append(new_p3)

    return phrase_alignment_list

if __name__=='__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-a", "--alignments",
        help="File containing alignments")
    arg_parser.add_argument("-l1", "--language1",
        help="File containing sentences of language 1")
    arg_parser.add_argument("-l2", "--language2",
        help="File containing sentences of language 2")
    
    args = arg_parser.parse_args()
    alignments = args.alignments
    language1 = args.language1
    language2 = args.language2
    print alignments, language1, language2
    phrase_pairs = extract_phrase_pairs(alignments, language1, language2)
