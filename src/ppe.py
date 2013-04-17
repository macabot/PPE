# phrase pair extractor

import argparse
from collections import Counter
import sys

def conditional_probabilities(phrase_pair_freqs, 
                              l1_phrase_freqs, l2_phrase_freqs):
    l1_given_l2 = {}
    l2_given_l1 = {}
    for phrase_pair, freq in phrase_pair_freqs.iteritems():
        l1_given_l2[phrase_pair] = freq / l1_phrase_freqs[phrase_pair[0]]
        l2_given_l1[phrase_pair] = freq / l2_phrase_freqs[phrase_pair[1]]

    return l1_given_l2, l2_given_l1

def phrase_probabilities(phrase_freqs):
    freq_sum = sum(phrase_freqs.values())
    phrase_probs = {}
    for phrase, freq in phrase_freqs.iteritems():
        phrase_probs[phrase] = freq / freq_sum

    return phrase_probs

def joint_probabilities(l1_given_l2, l2_phrase_probs):
    joint_probs = {}
    for phrase, prob in l1_given_l2.iteritems():
        joint_probs[phrase] = prob * l2_phrase_probs[phrase[1]]

    return joint_probs

def extract_phrase_pair_freqs(alignments, language1, language2, max_length = float('inf')):
    phrase_pair_freqs = Counter()
    l1_phrase_freqs = Counter()
    l2_phrase_freqs = Counter()
    alignments = open(alignments, 'r')
    language1 = open(language1, 'r')
    language2 = open(language2, 'r')
    
    for i, str_align in enumerate(alignments):
        if i%1000==0:
            sys.stdout.write('\r%d' % i)
            sys.stdout.flush()

        l1 = language1.next()
        l2 = language2.next()
        #print str_align, l1, l2
        phrase_alignments = extract_alignments(str_to_alignments(str_align), max_length)
        for phrase_pair in extract_phrase_pairs_gen(phrase_alignments, l1, l2):
            phrase_pair_freqs[phrase_pair] += 1
            l1_phrase_freqs[phrase_pair[0]] += 1
            l2_phrase_freqs[phrase_pair[1]] += 1

    alignments.close()
    language1.close()
    language2.close()
    sys.stdout.write('\n')
    return phrase_pair_freqs, l1_phrase_freqs, l2_phrase_freqs
    
def extract_phrase_pairs_gen(phrase_alignments, l1, l2):
    l1_words = l1.strip().split()
    l2_words = l2.strip().split()
    for min1, min2, max1, max2 in phrase_alignments:
        yield (' '.join(l1_words[min1:max1+1]), 
               ' '.join(l2_words[min2:max2+1]))
    
def str_to_alignments(string):
    string_list = string.strip().split()
    alignments = set([])
    for a_str in string_list:
        a1_str, a2_str = a_str.split('-')
        alignments.add((int(a1_str), int(a2_str)))

    return alignments

def phrase_alignment_expansions(phrase_alignments, max_length = float('inf')):
    min1, min2, max1, max2 = phrase_range(phrase_alignments)
    if max1-min1+1 > max_length or max2-min2+1 > max_length:
        return [], []

    range1 = range(min1, max1+1)
    range2 = range(min2, max2+1)
    for a1, a2 in phrase_alignments:
        if a1 in range1:
            range1.remove(a1)
        if a2 in range2:
            range2.remove(a2)

    return range1, range2
    
def phrase_range(phrase_alignments):
    min1 = min(a1 for (a1, a2) in phrase_alignments)
    min2 = min(a2 for (a1, a2) in phrase_alignments)
    max1 = max(a1 for (a1, a2) in phrase_alignments)
    max2 = max(a2 for (a1, a2) in phrase_alignments)
    return min1, min2, max1, max2

def extract_alignments(word_alignments, max_length = float('inf')):
    phrase_alignment_list = set([])
    # First form words into phrase pairs
    while len(word_alignments):        
        phrase_alignment_init = word_alignments.pop()
        phrase_alignment = set([phrase_alignment_init])
        phrase_alignment_exp = [[phrase_alignment_init[0]], [phrase_alignment_init[1]]]
        while phrase_alignment_exp[0] or phrase_alignment_exp[1]:
            added_points = set([(x,y) for (x,y) in word_alignments 
                            if (x in phrase_alignment_exp[0] or y in phrase_alignment_exp[1])])
            # stop if no alignment can fill the gaps
            if not added_points:
                break

            phrase_alignment |= added_points
            word_alignments -= added_points
            phrase_alignment_exp = phrase_alignment_expansions(phrase_alignment, max_length)

        range = phrase_range(phrase_alignment)
        if range[2]-range[0]+1 <= max_length and range[3]-range[1]+1 <= max_length:
            phrase_alignment_list.add(range)

    #Then loop over phrase pairs to join them together into new ones
    phrase_queue = set(phrase_alignment_list)
    phrase_alignment_list = set()
    while len(phrase_queue):
        p1 = phrase_queue.pop()
        new_p3 = set()
        for p2 in phrase_queue:
            p3 = None
            if p1[0] is p2[2]+1 and p1[1] is p2[3]+1:
                #p2 above, to the left of p1
                p3 = p2[0], p2[1], p1[2], p1[3]
            elif p1[2] is p2[0]-1 and p1[1] is p2[3]+1:
                #p2 above, to the right of p1
                p3 = p1[0], p2[1], p2[2], p1[3]
            elif p1[0] is p2[2]+1 and p1[3] is p2[1]-1:
                #p2 below, to the left of p1
                p3 = p2[0], p1[1], p1[2], p2[3]
            elif p1[2] is p2[0]-1 and p1[3] is p2[1]-1:
                #p2 below, to the right of p1
                p3 = p1[0], p1[1], p2[2], p2[3]
            # if p3 exists and is smaller or equal to the max length
            if p3 and p3[2]-p3[0]+1 <= max_length and p3[3]-p3[1]+1 <= max_length:
                new_p3.add(p3)

        phrase_alignment_list.add(p1)
        phrase_queue |= new_p3

    return phrase_alignment_list

def phrase_pairs_to_file(file_name, phrase_pairs, joint_probs,
                         l1_given_l2, l2_given_l1):
    out = open(file_name, 'w')
    for pair in phrase_pairs:
        joint = joint_probs[pair]
        l1_l2 = l1_given_l2[pair]
        l2_l1 = l2_given_l1[pair]
        out.write('%s %f %f %f\n' % (pair, joint, l1_l2, l2_l1))

    out.close()


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-a", "--alignments",
        help="File containing alignments")
    arg_parser.add_argument("-l1", "--language1",
        help="File containing sentences of language 1")
    arg_parser.add_argument("-l2", "--language2",
        help="File containing sentences of language 2")
    arg_parser.add_argument("-o", "--output",
        help="File name of output")
    
    args = arg_parser.parse_args()
    alignments = args.alignments
    language1 = args.language1
    language2 = args.language2
    output_name = args.output
    
    print 'alignments: %s' % alignments
    print 'language1: %s' % language1
    print 'language2: %s' % language2
    print 'output name: %s' % output_name
    
    freqs = extract_phrase_pair_freqs(alignments, language1, language2, 4)
    phrase_pair_freqs, l1_phrase_freqs, l2_phrase_freqs = freqs
    l1_given_l2, l2_given_l1 = conditional_probabilities(phrase_pair_freqs, 
                              l1_phrase_freqs, l2_phrase_freqs)
    l2_phrase_probs = phrase_probabilities(l2_phrase_freqs)
    joint_probs = joint_probabilities(l1_given_l2, l2_phrase_probs)
    phrase_pairs_to_file(output_name, phrase_pair_freqs, joint_probs,
                         l1_given_l2, l2_given_l1)
    out = open(output_name, 'w')

    
if __name__ == '__main__':
    main()
    #str_align = '9-0 9-1 10-2 11-3 12-4 12-5 8-6 14-7 15-7 16-8 17-9 18-10 19-11 20-12 21-12 12-13 13-13 22-14 23-15 24-16 4-17 26-18 26-19 27-19 27-20 27-21 28-21 29-22 30-23 31-24 32-25 33-26 34-27 35-29 36-30 37-31 37-32 39-33 38-34 38-35 39-35 40-36 42-37 43-38'
    #print extract_alignments(str_to_alignments(str_align))

    