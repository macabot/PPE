# phrase pair extractor

import argparse

def extract_phrase_pair_freqs(alignments, language1, language2):
    phrase_pairs = []
    alignments = open(alignments, 'r')
    language1 = open(language1, 'r')
    language2 = open(language2, 'r')
    return phrase_pairs

def extract_phrase_pairs(alignments):
    # First form words into phrase pairs
    while alignments:
        rect_init = alignments.pop()
        rect_exp = [[rect_init[0]], [rect_init[1]]]
        while not (rect_exp[0] or rect_exp[1]):
            added_points = [(x,y) for (x,y) in alignments if (x in rect_exp[0] or y in rect_exp[1])]
            rect.append(added_points)
            for point in added_points:
                alignments.delete()
            rect_exp = rect_expansions(rect)
    #Then loop over phrase pairs to join them together into new ones

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
