# phrase pair extractor

import argparse
from collections import Counter

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

def extract_phrase_pair_freqs(alignments, language1, language2):
    phrase_pair_freqs = Counter()
    l1_phrase_freqs = Counter()
    l2_phrase_freqs = Counter()
    alignments = open(alignments, 'r')
    language1 = open(language1, 'r')
    language2 = open(language2, 'r')
    for str_align, l1, l2 in alignments, language1, language2:
        phrase_alignments = extract_alignments(str_to_alignments(str_align))
        for phrase_pair in extract_phrase_pairs_gen(phrase_alignments, l1, l2):
            phrase_pair_freqs[phrase_pair] += 1
            l1_phrase_freqs[phrase_pair[0]] += 1
            l2_phrase_freqs[phrase_pair[1]] += 1

    alignments.close()
    language1.close()
    language2.close()
    return phrase_pair_freqs, l1_phrase_freqs, l2_phrase_freqs
    
def extract_phrase_pairs_gen(phrase_alignments, l1, l2):
    l1_words = l1.strip().split()
    l2_words = l2.strip().split()
    for min1, min2, max1, max2 in phrase_alignments:
        yield (l1_words[min1:max1+1], l2_words[min2:max2+1])
    
def str_to_alignments(string):
    string_list = string.strip().split()
    alignments = set([])
    for a_str in string_list:
        a1_str, a2_str = a_str.split('-')
        alignments.add((int(a1_str), int(a2_str)))

    return alignments

def phrase_alignment_expansions(phrase_alignments):
    min1, min2, max1, max2 = phrase_range(phrase_alignments)
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

def extract_alignments(word_alignments):
    phrase_alignment_list = set([])
    # First form words into phrase pairs
    while len(word_alignments):        
        phrase_alignment_init = word_alignments.pop()
        phrase_alignment = set([phrase_alignment_init])
        phrase_alignment_exp = [[phrase_alignment_init[0]], [phrase_alignment_init[1]]]
        while phrase_alignment_exp[0] or phrase_alignment_exp[1]:
            added_points = set([(x,y) for (x,y) in word_alignments if (x in phrase_alignment_exp[0] or y in phrase_alignment_exp[1])])
            phrase_alignment |= added_points
            word_alignments -= added_points
            phrase_alignment_exp = phrase_alignment_expansions(phrase_alignment)
        phrase_alignment_list.add(phrase_range(phrase_alignment))
    #Then loop over phrase pairs to join them together into new ones
    phrase_queue = list(phrase_alignment_list)
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
            if p3:
                new_p3.add(p3)
        phrase_alignment_list |= new_p3
        phrase_queue.extend(new_p3)

    return phrase_alignment_list

def phrase_pairs_to_file(file_name, phrase_pairs, joint_probs,
                         l1_given_l2, l2_given_l1):
    out = open(file_name, 'w')
    for pair in phrase_pairs:
        joint = joint_probs[pair]
        l1_l2 = l1_given_l2[pair]
        l2_l1 = l2_given_l1[pair]
        out.write('%s %f %f %f\n' % (pair,joint, l1_l2, l2_l1))

    out.close()


if __name__=='__main__':
    
    a = '0-0 1-1 2-2 2-3 1-4 3-5 3-6 4-7'
    phrase_pairs = extract_alignments(str_to_alignments(a))
    print phrase_pairs