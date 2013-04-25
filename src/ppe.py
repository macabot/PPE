# phrase pair extractor

"""
By Michael Cabot (6047262) and Sander Nugteren (6042023)
"""

import argparse
from collections import Counter
import sys

def conditional_probabilities(phrase_pair_freqs, 
                              l1_phrase_freqs, l2_phrase_freqs):
    """Calculate the conditional probability of phrase pairs in both directions.
    
    Keyword arguments:
    phrase_pair_freqs -- counter of phrase pairs
    l1_phrase_freqs -- counter of phrases in language 1
    l2_phraes_freqs -- counter of phrases in lanuage 2
    
    Returns 2 dictionaries mapping a phrase pair to P(l1 | l2) and P(l2 | l1)
    """
    l1_given_l2 = {}
    l2_given_l1 = {}
    for phrase_pair, freq in phrase_pair_freqs.iteritems():
        l1_given_l2[phrase_pair] = float(freq) / l1_phrase_freqs[phrase_pair[0]]
        l2_given_l1[phrase_pair] = float(freq) / l2_phrase_freqs[phrase_pair[1]]

    return l1_given_l2, l2_given_l1

def phrase_probabilities(phrase_freqs):
    """Calculate the probability of a phrase.
    
    Keyword arguments:
    phrase_freqs -- counter of phrases
    
    Returns a dictionary mapping a phrase to its probabilitly
    """
    freq_sum = sum(phrase_freqs.values())
    phrase_probs = {}
    for phrase, freq in phrase_freqs.iteritems():
        phrase_probs[phrase] = float(freq) / freq_sum

    return phrase_probs

def joint_probabilities(l1_given_l2, l2_phrase_probs):
    """Calculate the joint probability of a phrase pair:
    P(l1, l2) = P(l1 | l2) * P(l2)
    
    Keyword arguments:
    l1_given_l2 -- dictionary mapping a phrase pair (l1,l2) to its
                   conditional probability P(l1 | l2)
    l2_phrase_probs -- dictionary mapping a phraes to its probability
    
    Return a dictionary that maps a phrase pair to its joint probability
    """
    joint_probs = {}
    for phrase, prob in l1_given_l2.iteritems():
        joint_probs[phrase] = prob * l2_phrase_probs[phrase[1]]

    return joint_probs

def add_phrase_alignment(collection, phrase, max_length,
                         l1_length, l2_length):
    """Add a phrase alignment to a collection if:
    - its length is smaller or equal to the max length
    - the alignment is a contituent of the sentences
    
    Keyword arguments:
    collection -- a list or set
    phrase -- a 4-tuple (min1,min2,max1,max2) denoting the range of
              the constituents in language 1 and 2
    max_length -- the maximum length of a phrase in the phrase alignment
    l1_length -- the length of the sentence in language 1
    l2_length -- the length of teh sentence in language 2
    """
    if phrase and phrase[2] - phrase[0]+1 <= max_length \
              and phrase[3] - phrase[1]+1 <= max_length \
              and phrase[0] >= 0 and phrase[1] >= 0     \
              and phrase[2] < l1_length and phrase[3] < l2_length:
        if isinstance(collection, list):
            collection.append(phrase)
        elif isinstance(collection, set):
            collection.add(phrase)
        else:
            return NotImplemented

def extract_phrase_pair_freqs(alignments_file, language1_file,
                              language2_file, 
                              max_length = float('inf')):
    """Extract and count the frequency of all phrase pairs given an
    alignment between sentences.
    
    Keyword arguments:
    alignments_file -- file that contains the alignments
    language1_file -- file containing sentences from language 1
    language2_file -- file containing sentences from language 2
    max_length -- maximum length of phrase pairs
    
    Returns counter of phrase-pairs, counter of phrases in language1
            and counter of phrases in language2
    """
    phrase_pair_freqs = Counter()
    l1_phrase_freqs = Counter()
    l2_phrase_freqs = Counter()
    num_lines = number_of_lines(alignments_file)
    alignments = open(alignments_file, 'r')
    language1 = open(language1_file, 'r')
    language2 = open(language2_file, 'r')
    
    for i, str_align in enumerate(alignments):
        if i % (num_lines/100) is 0:
            sys.stdout.write('\r%d%%' % (i*100/num_lines,))
            sys.stdout.flush()

        l1 = language1.next()
        l2 = language2.next()
        #print str_align, l1, l2
        align = str_to_alignments(str_align)
        phrase_alignments = extract_alignments(align, len(l1), len(l2),
                                               max_length)
        
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
    """Given alignments, extract phrase pairs from 2 sentences
    
    Keyword arguments:
    phrase_alignments -- list of phraes alignments. A phrase alignment
                         is a 4 tuple denoting the range of the constituents
    l1 -- sentence in language 1
    l2 -- sentence in language 2
    
    Yield a 2-tuple containing a phrase pair
    """
    l1_words = l1.strip().split()
    l2_words = l2.strip().split()
    for min1, min2, max1, max2 in phrase_alignments:
        yield (' '.join(l1_words[min1:max1+1]), 
               ' '.join(l2_words[min2:max2+1]))
    
def str_to_alignments(string):
    """Parse an alignment from a string
    
    Keyword arguments:
    string -- contains alignment
    
    Return a set of 2-tuples. First value is index of word in language 1
           second value is index of word in language 2
    """
    string_list = string.strip().split()
    alignments = set()
    for a_str in string_list:
        a1_str, a2_str = a_str.split('-')
        alignments.add((int(a1_str), int(a2_str)))

    return alignments

def phrase_alignment_expansions(phrase_alignments, max_length = float('inf')):
    """For each language find the words that are not covered with the given
    phrase alignment.
    E.g. phrase_alignments = [(0,0), (2,0)]
    returns [1], []
    because index 1 in sentence 1 is not covered.
    
    Keyword arguments:
    phrase_alignments -- list of 2-tuples denoting the alignment between words
    max_length -- maximum length of a phrase alignment
    
    Returns 2 lists of indexes that are not covered
    """
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
    """Calcualte the range of a phrase alignment
    
    Keyword arguments:
    phrase_alignments -- list of 2-tuples denoting the alignment between words
    
    Returns a 4-tuples denoting the range of the phrase alignment
    """
    min1 = min2 = float('inf')
    max1 = max2 = float('-inf')
    for (a1, a2) in phrase_alignments:
        if a1 < min1:
            min1 = a1
        if a1 > max1:
            max1 = a1
        if a2 < min2:
            min2 = a2
        if a2 > max2:
            max2 = a2

    return min1, min2, max1, max2

def extract_alignments(word_alignments, l1_length, l2_length,
                       max_length = float('inf')):
    """Extracts all alignments between 2 sentences given a word alignment
    
    Keyword arguments:
    word_alignemnts -- set of 2-tuples denoting alignment between words in 
                       2 sentences
    l1_length -- length of sentence 1
    l2_length -- length of sentence 2
    max_length -- maximum length of a phrase pair
    
    Returns set of 4-tuples denoting the range of phrase_alignments
    """
    phrase_queue = set()
    #copy to use later for singletons
    word_alignments_orig = set(word_alignments)
    # First form words into phrase pairs
    while len(word_alignments):        
        phrase_alignment_init = word_alignments.pop()
        phrase_alignment = set([phrase_alignment_init])
        phrase_alignment_exp = [[phrase_alignment_init[0]], 
                                [phrase_alignment_init[1]]]
        while phrase_alignment_exp[0] or phrase_alignment_exp[1]:
            added_points = set([(x, y) for (x, y) in word_alignments 
                            if (x in phrase_alignment_exp[0] 
                            or y in phrase_alignment_exp[1])])
            # stop if no alignment can fill the gaps
            if not added_points:
                break

            phrase_alignment |= added_points
            word_alignments -= added_points
            phrase_alignment_exp = phrase_alignment_expansions(phrase_alignment, max_length)

        align_range = phrase_range(phrase_alignment)
        add_phrase_alignment(phrase_queue, align_range, max_length,
                             l1_length, l2_length)

    #Then loop over phrase pairs to join them together into new ones
    phrase_alignment_list = set()
    while len(phrase_queue):
        p1 = phrase_queue.pop()
        new_p3 = set()
        singletons = True
        #add singletons
        singleton = set([(x, y) for (x, y) in word_alignments_orig 
            if x is p1[0]-1])
        if not singleton:
            p3 = p1[0]-1, p1[1], p1[2], p1[3]
            add_phrase_alignment(new_p3, p3, max_length, 
                                 l1_length, l2_length)
        singleton = set([(x, y) for (x, y) in word_alignments_orig 
            if x is p1[2]+1])
        if not singleton:
            p3 = p1[0], p1[1], p1[2]+1, p1[3]
            add_phrase_alignment(new_p3, p3, max_length, 
                                 l1_length, l2_length)
        singleton = set([(x, y) for (x, y) in word_alignments_orig 
            if y is p1[1]-1])
        if not singleton:
            p3 = p1[0], p1[1]-1, p1[2], p1[3]
            add_phrase_alignment(new_p3, p3, max_length,
                                 l1_length, l2_length)
        singleton = set([(x, y) for (x, y) in word_alignments_orig 
            if y is p1[3]+1])
        if not singleton:
            p3 = p1[0], p1[1], p1[2], p1[3]+1
            add_phrase_alignment(new_p3, p3, max_length,
                                 l1_length, l2_length)

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
            add_phrase_alignment(new_p3, p3, max_length,
                                 l1_length, l2_length)

        phrase_alignment_list.add(p1)
        phrase_queue |= new_p3

    return phrase_alignment_list

def phrase_pairs_to_file(file_name, phrase_pairs, joint_probs,
                         l1_given_l2, l2_given_l1):
    """Write phrase pairs and their joint and conditional probabilities to a file
    
    Keyword arguments:
    file_name -- name of file for writing
    phrase_pairs -- list of phrase pairs
    joint_probs -- dictionary mapping phrase pair to its joints probability
    l1_given_l2 -- dictionary mapping phrase pair (l1,l2) to is conditional 
                   probability P(l1 | l2)
    l2_given_l1 -- dictionary mapping phrase pair (l1,l2) to is conditional 
                   probability P(l2 | l1)
    """
    out = open(file_name, 'w')
    for pair in phrase_pairs:
        joint = joint_probs[pair]
        l1_l2 = l1_given_l2[pair]
        l2_l1 = l2_given_l1[pair]
        out.write('(%s, %s, %s, %s)\n' % (pair, joint, l1_l2, l2_l1))

    out.close()

def number_of_lines(file_name):
    """Counts the number of lines in a file
    
    Keywords arguments:
    file_name -- name of file
    
    Returns number of lines
    """
    amount = 0
    file = open(file_name, 'r')
    for _ in file:
        amount += 1

    return amount

def main():
    """Read the following arguments from the cmd line:
    - name of file containing the alignments
    - name of file containing sentence of language 1
    - name of file containing sentence of language 2
    - name of file for writing output
    - maximum length of a phrase pair
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-a", "--alignments",
        help="File containing alignments")
    arg_parser.add_argument("-l1", "--language1",
        help="File containing sentences of language 1")
    arg_parser.add_argument("-l2", "--language2",
        help="File containing sentences of language 2")
    arg_parser.add_argument("-o", "--output",
        help="File name of output")
    arg_parser.add_argument("-m", "--max_length",
        help="Maximum length of phrase pairs")
    
    args = arg_parser.parse_args()
    alignments = args.alignments
    language1 = args.language1
    language2 = args.language2
    output_name = args.output
    max_length = int(args.max_length)
    
    print 'alignments: %s' % alignments
    print 'language1: %s' % language1
    print 'language2: %s' % language2
    print 'output name: %s' % output_name
    print 'max length: %s'  % max_length
    
    freqs = extract_phrase_pair_freqs(alignments, language1, language2, max_length)
    phrase_pair_freqs, l1_phrase_freqs, l2_phrase_freqs = freqs
    l1_given_l2, l2_given_l1 = conditional_probabilities(phrase_pair_freqs, 
                              l1_phrase_freqs, l2_phrase_freqs)
    l2_phrase_probs = phrase_probabilities(l2_phrase_freqs)
    joint_probs = joint_probabilities(l1_given_l2, l2_phrase_probs)
    phrase_pairs_to_file(output_name, phrase_pair_freqs, joint_probs,
                         l1_given_l2, l2_given_l1)

    
if __name__ == '__main__':
    main()
