# phrase pair extractor

import argparse

def extract_phrase_pairs(alignments, language1, language2):
    phrase_pairs = []
    # TODO
    return phrase_pairs

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