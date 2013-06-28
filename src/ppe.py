# phrase pair extractor

"""
By Michael Cabot (6047262) and Sander Nugteren (6042023)
"""

import argparse
from collections import Counter
import sys
import pickle

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
    num_lines = len(phrase_pair_freqs)
    for i, (phrase_pair, freq) in enumerate(phrase_pair_freqs.iteritems()):
        if i % (num_lines/100) == 0:
            sys.stdout.write('\r%d%%' % (i*100/num_lines,))
            sys.stdout.flush()

        try:
            l1_given_l2[phrase_pair] = float(freq) / l1_phrase_freqs[phrase_pair[0]]
            l2_given_l1[phrase_pair] = float(freq) / l2_phrase_freqs[phrase_pair[1]]
        except:
            print 'phrase pair: %s' % (phrase_pair,)
            print 'i: %s' % i
            raise

    sys.stdout.write('\n')
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
    if phrase != None and phrase[2] - phrase[0]+1 <= max_length \
            and phrase[3] - phrase[1]+1 <= max_length \
            and phrase[0] >= 0 and phrase[1] >= 0 \
            and phrase[2] < l1_length and phrase[3] < l2_length:
        if isinstance(collection, list):
            collection.append(phrase)
        elif isinstance(collection, set):
            collection.add(phrase)
        else:
            return NotImplemented

def extract_phrase_pair_freqs(alignments_file, language1_file,
                              language2_file, max_length,
                              sentence_weights_file = None):
    """Extract and count the frequency of all phrase pairs given an
    alignment between sentences.

    Keyword arguments:
    alignments_file -- file that contains the alignments
    language1_file -- file containing sentences from language 1
    language2_file -- file containing sentences from language 2
    max_length -- maximum length of phrase pairs
    sentence_weights -- file containing weights for each sentence pair

    Returns counter of phrase-pairs, counter of phrases in language1
            and counter of phrases in language2
    """
    # phrase frequencies
    phrase_pair_freqs = Counter()
    l1_phrase_freqs = Counter()
    l2_phrase_freqs = Counter()
    # lexical frequencies
    lex_pair_freqs = Counter()
    l1_lex_freqs = Counter()
    l2_lex_freqs = Counter()
    # open files
    num_lines = number_of_lines(alignments_file)
    alignments = open(alignments_file, 'r')
    language1 = open(language1_file, 'r')
    language2 = open(language2_file, 'r')
    if sentence_weights_file:
        sentence_weights = open(sentence_weights_file, 'r')

    if num_lines/100 == 0:
        frac = 1
    else:
        frac = num_lines/100
    for i, str_align in enumerate(alignments):
        if i % frac == 0:
            sys.stdout.write('\r%d%%' % (i*100/num_lines,))
            sys.stdout.flush()

        l1_words = language1.next().strip().split()
        l2_words = language2.next().strip().split()
        l1_length = len(l1_words)
        l2_length = len(l2_words)
        if sentence_weights_file:
            weight = float(sentence_weights.next().strip())
        else:
            weight = 1

        align = str_to_alignments(str_align)
        phrase_alignments = extract_alignments(set(align), l1_length,
            l2_length, max_length)

        for phrase_pair in extract_phrase_pairs_gen(phrase_alignments,
                                                    l1_words, l2_words):
            phrase_pair_freqs[phrase_pair] += weight
            l1_phrase_freqs[phrase_pair[0]] += weight
            l2_phrase_freqs[phrase_pair[1]] += weight
            if len(phrase_pair[0].split()) == len(phrase_pair[1].split()) == 1:
                lex_pair_freqs[phrase_pair] += weight
                l1_lex_freqs[phrase_pair[0]] += weight
                l2_lex_freqs[phrase_pair[1]] += weight

        unaligned, unaligned2 = unaligned_words(align, l1_length, l2_length)
        unaligned.extend(unaligned2)
        for phrase_pair in unaligned_phrase_pairs_gen(unaligned, l1_words,
                                                      l2_words):
            #phrase_pair_freqs[phrase_pair] += weight
            #l1_phrase_freqs[phrase_pair[0]] += weight
            #l2_phrase_freqs[phrase_pair[1]] += weight
            lex_pair_freqs[phrase_pair] += weight
            l1_lex_freqs[phrase_pair[0]] += weight
            l2_lex_freqs[phrase_pair[1]] += weight

    alignments.close()
    language1.close()
    language2.close()
    if sentence_weights_file:
        sentence_weights.close()

    sys.stdout.write('\n')
    return ((phrase_pair_freqs, l1_phrase_freqs, l2_phrase_freqs),
            (lex_pair_freqs, l1_lex_freqs, l2_lex_freqs))

def extract_phrase_pairs_gen(phrase_alignments, l1_words, l2_words):
    """Given alignments, extract phrase pairs from 2 sentences

    Keyword arguments:
    phrase_alignments -- list of phraes alignments. A phrase alignment
                         is a 4 tuple denoting the range of the constituents
    l1_words -- words in language 1
    l2_words -- words in language 2

    Yield a 2-tuple containing a phrase pair
    """
    for min1, min2, max1, max2 in phrase_alignments:
        yield (' '.join(l1_words[min1:max1+1]),
               ' '.join(l2_words[min2:max2+1]))

def unaligned_phrase_pairs_gen(unaligned, l1_words, l2_words):
    """For unaligned words create an alignment with 'NULL'."""
    for (a1, a2) in unaligned:
        if a1 == None:
            yield ('NULL', l2_words[a2])
        elif a2 == None:
            yield (l1_words[a1], 'NULL')

def str_to_alignments(string):
    """Parse an alignment from a string

    Keyword arguments:
    string -- contains alignment

    Return a set of 2-tuples. First value is index of word in language 1
           second value is index of word in language 2
    """
    string_list = string.strip().split()
    alignments = []
    for a_str in string_list:
        a1_str, a2_str = a_str.split('-')
        alignments.append((int(a1_str), int(a2_str)))

    return alignments

def phrase_alignment_expansions(phrase_alignments, word_alignments, max_length):
    """For each language find the alignments belonging to the words that are
    not covered with the given phrase alignment."""
    min1, min2, max1, max2 = phrase_range(phrase_alignments)
    if max1-min1+1 > max_length or max2-min2+1 > max_length:
        return set([])

    return set([(a1, a2) for (a1, a2) in word_alignments
        if (a1, a2) not in phrase_alignments and
        (min1 <= a1 <= max1 or min2 <= a2 <= max2)])

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

def extract_alignments3(word_alignments, l1_length, l2_length, max_length):
    """Extract all alignments between 2 sentence given a word alignment."""
    phrase_alignments = set([])
    prev_center = (-1, -1)
    for i, center in enumerate(word_alignments):
        if i > 0:
            prev_center = word_alignments[i-1]

        span1_max = l1_length - (prev_center[0]+1)
        for span1_size in xrange(1, span1_max):
            if span1_size > max_length:
                break
            for p1_min in xrange(center[0]-span1_size+1, center[0]+span1_size):
                p1_max = p1_min + span1_size - 1
                span2_max = l2_length - (prev_center[1]+1)
                for span2_size in xrange(1, span2_max):
                    if span2_size > max_length:
                        break
                    for p2_min in xrange(center[1]-span2_size+1,
                            center[1]+span2_size):
                        p2_max = p2_min + span2_size - 1

                        phrase_alignment = (p1_min, p2_min, p1_max, p2_max)
                        if is_valid_phrase_alignment(phrase_alignment,
                                word_alignments, max_length):
                            phrase_alignments.add(phrase_alignment)

    # add word alignments
    phrase_alignments |= set([phrase_range([a]) for a in word_alignments])
    return phrase_alignments

def extract_alignments2(word_alignments, l1_length, l2_length, max_length):
    """Extract all alignments between 2 sentence given a word alignment.
    phrase_range = (p1_min, p2_min, p1_max, p2_max)"""
    phrase_alignments = set([])
    for span1_size in xrange(1, l1_length):
        if span1_size > max_length:
            break
        for p1_min in xrange(l1_length - span1_size):
            p1_max = p1_min + span1_size - 1
            for span2_size in xrange(1, l2_length):
                if span2_size > max_length:
                    break
                for p2_min in xrange(l2_length - span2_size):
                    p2_max = p2_min + span2_size - 1
                    phrase_alignment = (p1_min, p2_min, p1_max, p2_max)
                    if is_valid_phrase_alignment(phrase_alignment,
                            word_alignments, max_length):
                        phrase_alignments.add(phrase_alignment)

    # add word alignments
    phrase_alignments |= set([phrase_range([a]) for a in word_alignments])
    return phrase_alignments
    '''
    for span_size in xrange(2, len(word_alignments)+1): # loop over spans sizes
        for i in xrange(len(word_alignments)-span_size+1):
            j = i+span_size
            word_align_slice = word_alignments[i:j]
            # add valid phrase alignments
            if is_valid_phrase(word_align_slice, word_alignments, max_length):
                phrase_alignments.add(phrase_range(word_align_slice))

    # add word alignments
    phrase_alignments |= set([phrase_range([a]) for a in word_alignments])
    return phrase_alignments
    '''

def is_valid_phrase_alignment((min1, min2, max1, max2), word_alignments,
        max_length):
    if max1-min1+1 > max_length or max2-min2+1 > max_length:
        return False

    word_align_slice = [(a1, a2)
                        for (a1, a2) in word_alignments
                        if min1 <= a1 <= max1 or min2 <= a2 <= max2]
    if len(word_align_slice) == 0:
        return False

    for (a1, a2) in word_alignments:
        if (a1, a2) not in word_align_slice and \
                (min1 <= a1 <= max1 or min2 <= a2 <= max2):
            return False

    return True

def is_valid_phrase(word_align_slice, word_alignments, max_length):
    """Check whether a span is contigious"""
    if len(word_align_slice) == 0:
        return False

    min1, min2, max1, max2 = phrase_range(word_align_slice)
    if max1-min1+1 > max_length or max2-min2+1 > max_length:
        return False

    for (a1, a2) in word_alignments:
        if (a1, a2) not in word_align_slice and \
                (min1 <= a1 <= max1 or min2 <= a2 <= max2):
            return False

    return True

def extract_alignments_old(word_alignments, l1_length, l2_length,
                       max_length): # TODO remove?
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
        temp_word_alignments = set(word_alignments_orig)
        expansion_points = phrase_alignment_expansions(phrase_alignment,
            temp_word_alignments, max_length)
        while expansion_points:
            phrase_alignment |= expansion_points
            temp_word_alignments -= expansion_points
            expansion_points = phrase_alignment_expansions(phrase_alignment,
                temp_word_alignments, max_length)

        align_range = phrase_range(phrase_alignment)
        add_phrase_alignment(phrase_queue, align_range, max_length,
                             l1_length, l2_length)

    # loop over phrase pairs to join them together into new ones
    phrase_alignment_list = set() # TODO should be array?
    # TODO turn phrase_alignment_list into phrase_queue untill it does not
    # not change in size
    '''
    TODO dynamic programming
    A = 0-0
    B = 1-1, 1-2, 2-1, 2-3
    C = 3-5
    D = 4-4
    E = 5-6
    y=valid, n=invalid
    y(A_E)
    y(A_D)  y(B_E)
    n(A_C)  y(B_D)  y(C_E)
    y(A_B)  n(B_C)  y(C_D)  n(D_E)

    create tree bottom-up
    extract phrase pairs that are valid
    '''
    while len(phrase_queue):
        p1 = phrase_queue.pop()
        new_p3 = set()
        #add singletons
        singleton = set([(x, y) for (x, y) in word_alignments_orig
            if x == p1[0]-1])
        if not singleton:
            p3 = p1[0]-1, p1[1], p1[2], p1[3]
            add_phrase_alignment(new_p3, p3, max_length,
                                 l1_length, l2_length)
        singleton = set([(x, y) for (x, y) in word_alignments_orig
            if x == p1[2]+1])
        if not singleton:
            p3 = p1[0], p1[1], p1[2]+1, p1[3]
            add_phrase_alignment(new_p3, p3, max_length,
                                 l1_length, l2_length)
        singleton = set([(x, y) for (x, y) in word_alignments_orig
            if y == p1[1]-1])
        if not singleton:
            p3 = p1[0], p1[1]-1, p1[2], p1[3]
            add_phrase_alignment(new_p3, p3, max_length,
                                 l1_length, l2_length)
        singleton = set([(x, y) for (x, y) in word_alignments_orig
            if y == p1[3]+1])
        if not singleton:
            p3 = p1[0], p1[1], p1[2], p1[3]+1
            add_phrase_alignment(new_p3, p3, max_length,
                                 l1_length, l2_length)

        for p2 in phrase_queue:
            p3 = None
            if p1[0] == p2[2]+1 and p1[1] == p2[3]+1:
                #p2 above, to the left of p1
                p3 = p2[0], p2[1], p1[2], p1[3]
            elif p1[2] == p2[0]-1 and p1[1] == p2[3]+1:
                #p2 above, to the right of p1
                p3 = p1[0], p2[1], p2[2], p1[3]
            elif p1[0] == p2[2]+1 and p1[3] == p2[1]-1:
                #p2 below, to the left of p1
                p3 = p2[0], p1[1], p1[2], p2[3]
            elif p1[2] == p2[0]-1 and p1[3] == p2[1]-1:
                #p2 below, to the right of p1
                p3 = p1[0], p1[1], p2[2], p2[3]
            # if p3 exists and is smaller or equal to the max length
            add_phrase_alignment(new_p3, p3, max_length, l1_length, l2_length)

        phrase_alignment_list.add(p1)
        phrase_queue |= new_p3

    # add word alignments
    phrase_alignment_list |= set([phrase_range([a])
                                  for a in word_alignments_orig])
    return phrase_alignment_list

def extract_alignments(word_alignments, l1_length, l2_length, max_length):
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
        temp_word_alignments = set(word_alignments_orig)
        expansion_points = phrase_alignment_expansions(phrase_alignment,
            temp_word_alignments, max_length)
        while expansion_points:
            phrase_alignment |= expansion_points
            temp_word_alignments -= expansion_points
            expansion_points = phrase_alignment_expansions(phrase_alignment,
                temp_word_alignments, max_length)

        align_range = phrase_range(phrase_alignment)
        add_phrase_alignment(phrase_queue, align_range, max_length,
                             l1_length, l2_length)

    # loop over phrase pairs to join them together into new ones
    phrase_alignment_list = set()
    while len(phrase_queue):
        p1 = phrase_queue.pop()
        new_p3 = set()
        #add singletons
        singleton = set([(x, y) for (x, y) in word_alignments_orig
            if x == p1[0]-1])
        if not singleton:
            p3 = p1[0]-1, p1[1], p1[2], p1[3]
            add_phrase_alignment(new_p3, p3, max_length,
                                 l1_length, l2_length)
        singleton = set([(x, y) for (x, y) in word_alignments_orig
            if x == p1[2]+1])
        if not singleton:
            p3 = p1[0], p1[1], p1[2]+1, p1[3]
            add_phrase_alignment(new_p3, p3, max_length,
                                 l1_length, l2_length)
        singleton = set([(x, y) for (x, y) in word_alignments_orig
            if y == p1[1]-1])
        if not singleton:
            p3 = p1[0], p1[1]-1, p1[2], p1[3]
            add_phrase_alignment(new_p3, p3, max_length,
                                 l1_length, l2_length)
        singleton = set([(x, y) for (x, y) in word_alignments_orig
            if y == p1[3]+1])
        if not singleton:
            p3 = p1[0], p1[1], p1[2], p1[3]+1
            add_phrase_alignment(new_p3, p3, max_length,
                                 l1_length, l2_length)

        # combine phrase alignments
        for p2 in phrase_queue:
            p3 = combine_phrase_alignments(p1, p2)
            p3 = fix_phrase_alignment(p3, word_alignments_orig, max_length)
            if p3 != p1:
                add_phrase_alignment(new_p3, p3, max_length, l1_length,
                                     l2_length)

        phrase_alignment_list.add(p1)
        phrase_queue |= new_p3

    # add word alignments
    phrase_alignment_list |= set([phrase_range([a])
                                  for a in word_alignments_orig])

    return phrase_alignment_list

def unaligned_words(word_alignments, l1_length, l2_length):
    """Find unaligned words."""
    aligned1 = set([])
    aligned2 = set([])
    for (a1, a2) in word_alignments:
        aligned1.add(a1)
        aligned2.add(a2)

    unaligned1 = [(a1, None) for a1 in set(range(l1_length)) - aligned1]
    unaligned2 = [(None, a2) for a2 in set(range(l2_length)) - aligned2]

    return unaligned1, unaligned2

def combine_phrase_alignments(p1, p2):
    """Combine to phrase alignments."""
    return (min(p1[0], p2[0]), min(p1[1], p2[1]),
        max(p1[2], p2[2]), max(p1[3], p2[3]))

def fix_phrase_alignment(phrase, word_alignments, max_length):
    """Fix discontiguous phrase alignments."""
    expansion_points = [(a1, a2) for (a1, a2) in word_alignments
        if partial_in_alignment((a1, a2), phrase)]
    while expansion_points:
        expansion_range = phrase_range(expansion_points)
        phrase = combine_phrase_alignments(phrase, expansion_range)
        if phrase[2]-phrase[0]+1 > max_length or \
                phrase[3]-phrase[1]+1 > max_length:
            return None

        expansion_points = [(a1, a2) for (a1, a2) in word_alignments
            if partial_in_alignment((a1, a2), phrase)]

    return phrase

def word_in_alignment(word, alignment):
    """Check whether a word alignment is inside a phrase alignment."""
    return alignment[0] <= word[0] <= alignment[2] and \
        alignment[1] <= word[1] <= alignment[3]

def partial_in_alignment(word, alignment):
    return (alignment[0] <= word[0] <= alignment[2]) != \
           (alignment[1] <= word[1] <= alignment[3])

def lex_pairs_to_file(file_name, l1_given_l2, l2_given_l1, lex_file):
    """Write lexical pairs and their conditional probabilities to a file."""
    lex_f2e = open("%s_lex_f2e" % file_name, 'w')
    lex_e2f = open("%s_lex_e2f" % file_name, 'w')
    old_lex = open(lex_file, 'r')
    num_lines = number_of_lines(lex_file)
    for i, line in enumerate(old_lex):
        if i % (num_lines/100) == 0:
            sys.stdout.write('\r%d%%' % (i*100/num_lines,))
            sys.stdout.flush()

        try:
            fields = line.strip().split()
            pair = tuple(fields[0:2])
            l1_l2 = l1_given_l2[pair]
            l2_l1 = l2_given_l1[pair]
            lex_f2e.write("%s %s %s\n" % (pair[1], pair[0], l2_l1))
            lex_e2f.write("%s %s %s\n" % (pair[0], pair[1], l1_l2))
        except:
            print 'line: %s' % line
            print 'i: %s' % i
            raise

    lex_f2e.close()
    lex_e2f.close()
    old_lex.close()
    sys.stdout.write('\n')

def phrase_pairs_to_file(file_name, phrase_l1_given_l2, phrase_l2_given_l1, lex_l1_given_l2,
        lex_l2_given_l1, phrase_table_file):
    """Write phrase pairs and their conditional probabilities to a file.

    Keyword arguments:
    file_name -- name of file for writing
    phrase_l1_given_l2 -- dictionary mapping phrase pair (l1,l2) to is conditional
                   probability P(l1 | l2) for phrase pairs
    phrase_l2_given_l1 -- dictionary mapping phrase pair (l1,l2) to is conditional
                   probability P(l2 | l1) for phrase pairs
    lex_l1_given_l2 -- same as phrsae_l1_given_l2 but for word pairs
    lex_l2_given_l1 -- same as phrsae_l2_given_l1 but for word pairs
    phrase_table_file -- file containing phrase table
    """
    phrase_table = open("%s_phrase-table.txt" % file_name, 'w')
    old_phrase_table = open(phrase_table_file, 'r')
    num_lines = number_of_lines(phrase_table_file)

    for i, line in enumerate(old_phrase_table):
        if i % (num_lines/100) == 0:
            sys.stdout.write('\r%d%%' % (i*100/num_lines,))
            sys.stdout.flush()

        try:
            fields = line.strip().split(" ||| ")
            pair = tuple(fields[0:2])
            l1_l2 = phrase_l1_given_l2[pair]
            l2_l1 = phrase_l2_given_l1[pair]
            alignment = str_to_alignments(fields[3])
            lex_l1_l2, lex_l2_l1 = calc_lexical_weights(lex_l1_given_l2, 
                lex_l2_given_l1, pair, alignment)

            phrase_table.write("%s ||| %s %s %s %s 2.718 ||| %s\n" %
                (" ||| ".join(fields[0:2]), l1_l2, lex_l1_l2, l2_l1, lex_l2_l1,
                " ||| ".join(fields[3:])))
        except:
            print 'line: %s' % line
            print 'i: %s ' % i
            raise

    phrase_table.close()
    old_phrase_table.close()
    sys.stdout.write('\n')

def calc_lexical_weights(l1_given_l2, l2_given_l1, pair, alignment):
    l1_words = pair[0].split()
    l2_words = pair[1].split()
    lex_l1_l2 = 1
    lex_l2_l1 = 1
    # aligned words
    for i1, i2 in alignment:
        lex_l1_l2 *= l1_given_l2[(l1_words[i1], l2_words[i2])]
        lex_l2_l1 *= l2_given_l1[(l1_words[i1], l2_words[i2])]

    # words with no alignments
    unaligned, unaligned2 = unaligned_words(alignment, len(l1_words),
        len(l2_words))
    unaligned.extend(unaligned2)
    for i1, i2 in unaligned:
        if i1 == None:
            i1_word = 'NULL'
            i2_word = l2_words[i2]
        elif i2 == None:
            i1_word = l1_words[i1]
            i2_word = 'NULL'

        lex_l1_l2 *= l1_given_l2[(i1_word, i2_word)]
        lex_l2_l1 *= l2_given_l1[(i1_word, i2_word)]

    return lex_l1_l2, lex_l2_l1

def number_of_lines(file_name):
    """Counts the number of lines in a file

    Keywords arguments:
    file_name -- name of file

    Returns number of lines
    """
    amount = 0
    doc = open(file_name, 'r')
    for _ in doc:
        amount += 1

    doc.close()
    return amount

def get_phrase_pair_alignments(file_name):
    """Read phrase pair alignments from a file"""
    phrase_pairs = {}
    phrase_pairs_file = open(file_name, 'r')
    for line in phrase_pairs_file:
        phrase1, phrase2, alignment = line.strip().split(" ||| ")
        phrase_pairs[(phrase1, phrase2)] = alignment

    phrase_pairs_file.close()
    return phrase_pairs

def freqs_to_file(file_name, freqs):
    phrase_pair_freqs, l1_phrase_freqs, l2_phrase_freqs = freqs
    doc_phrase_pairs = open("%s.pairs" % file_name, 'w')
    doc_l1_phrases = open("%s.l1-phrases" % file_name, 'w')
    doc_l2_phrases = open("%s.l2-phrases" % file_name, 'w')
    for phrase_pair, freq in phrase_pair_freqs.iteritems():
        doc_phrase_pairs.write("%s ||| %s ||| %s\n" %
                              (phrase_pair[0], phrase_pair[1], freq))
    for phrase, freq in l1_phrase_freqs.iteritems():
        doc_l1_phrases.write("%s ||| %s\n" % (phrase, freq))
    for phrase, freq in l2_phrase_freqs.iteritems():
        doc_l2_phrases.write("%s ||| %s\n" % (phrase, freq))

    doc_phrase_pairs.close()
    doc_l1_phrases.close()
    doc_l2_phrases.close()

def main():
    """Read the following arguments from the cmd line:
    - name of file containing the alignments
    - name of file containing sentence of language 1
    - name of file containing sentence of language 2
    - name of file for writing output
    - maximum length of a phrase pair
    """
    print 'Start...'

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-a", "--alignments", required=True,
        help="File containing alignments")
    arg_parser.add_argument("-l1", "--language1", required=True,
        help="File containing sentences of language 1")
    arg_parser.add_argument("-l2", "--language2", required=True,
        help="File containing sentences of language 2")
    arg_parser.add_argument("-o", "--output", required=True,
        help="File name of output")
    arg_parser.add_argument("-m", "--max_length",
        help="Maximum length of phrase pairs")
    arg_parser.add_argument("-w", "--sentence_weights",
        help="File containing the weight of each sentence pair.")
    arg_parser.add_argument("-pt", "--phrase_table", required=True,
        help="File containing phrase table.")
    arg_parser.add_argument("-lex", "--lex_pairs", required=True,
        help="File containing lexical pairs. e2f")
    arg_parser.add_argument("-pickle", "--pickle", action='store_true', 
        default=False, help="Pickle or unpickle freqs.")

    args = arg_parser.parse_args()
    alignments = args.alignments
    language1 = args.language1
    language2 = args.language2
    output_name = args.output
    phrase_table_file = args.phrase_table
    lex_file = args.lex_pairs
    if args.max_length:
        max_length = int(args.max_length)
    else: # if not specified, max phrase pair length is infinite
        max_length = float('inf')
    if args.sentence_weights:
        sentence_weights = args.sentence_weights
    else:
        sentence_weights = None

    print 'alignments: %s' % alignments
    print 'language1: %s' % language1
    print 'language2: %s' % language2
    print 'phrase table: %s' % phrase_table_file
    print 'lex file (e2f): %s' % lex_file
    print 'output name: %s' % output_name
    print 'max length: %s'  % max_length
    print ''

    print 'extract phrase pairs'
    if args.pickle:
        try:
            pickle_file = open("freqs.pickle", 'r')
            phrase_freqs, lex_freqs = pickle.load(pickle_file)
        except:
            print 'Could not find/read freqs.pickle. Creating a new one.'
            phrase_freqs, lex_freqs = extract_phrase_pair_freqs(alignments, 
                language1, language2, max_length, sentence_weights)
            pickle_file = open("freqs.pickle", 'w')
            pickle.dump((phrase_freqs, lex_freqs), pickle_file)
    else:
        phrase_freqs, lex_freqs = extract_phrase_pair_freqs(alignments, language1, language2,
            max_length, sentence_weights)

    print 'freqs to file'
    freqs_to_file("extracted_phrase_pairs.temp", phrase_freqs)
    freqs_to_file("extracted_lex_pairs.temp", lex_freqs)
    phrase_pair_freqs, l1_phrase_freqs, l2_phrase_freqs = phrase_freqs
    lex_pair_freqs, l1_lex_freqs, l2_lex_freqs = lex_freqs

    print 'calculate phrase conditional probabilities'
    phrase_l1_given_l2, phrase_l2_given_l1 = conditional_probabilities(phrase_pair_freqs,
                              l1_phrase_freqs, l2_phrase_freqs)

    print 'calculate lex conditional probabilities'
    lex_l1_given_l2, lex_l2_given_l1 = conditional_probabilities(lex_pair_freqs,
                              l1_lex_freqs, l2_lex_freqs)

    print 'phrase pairs to file'
    phrase_pairs_to_file(output_name, phrase_l1_given_l2, phrase_l2_given_l1, 
        lex_l1_given_l2, lex_l2_given_l1, phrase_table_file)

    print 'lexical pairs to file'
    lex_pairs_to_file(output_name, lex_l1_given_l2, lex_l2_given_l1, lex_file)

    print 'Done.'

def test():
    """For testing purposes."""
    l1_list = ["( applaudissements du groupe PSE ) ",
        "la concentration scandaleuse de pouvoir dans des secteurs d&apos; importance strategique livre a des multinationales uniquement soucieuses de profit l&apos; economie d&apos; Etats tout entiers - et d&apos; Etats membres de l&apos; Union ! ",
        "nous avons considere ce probleme , pensez-vous ! nous l&apos; avons considere et le passons au crible avec une grande attention , notamment grace aux inquietudes que vous avez exposees . ",
        "a cet egard , on peut , pour utiliser une expression bien francaise , dire franchement &quot; Chapeau ! &quot; a l&apos; Union europeenne . ",
        "dans son rapport , Mme Flautre souligne egalement un domaine ou il y a un manque cruel de coordination , alors qu&apos; on en a desesperement besoin . "]
    l2_list = ["( applause from the PSE Group ) ",
        "the scandalous concentration of power in sectors of strategic importance is giving speculative multinational groups economies the size of entire states , and Member States of the Union at that . ",
        "of course we have pondered this issue , and we are still studying it extremely carefully , and this is also thanks to the concerns you have voiced . ",
        "in this connection , French speakers would speak of a &quot; coup de chapeau &quot; : in other words , I take my hat off to the EU . ",
        "in her report , Mrs Flautre also drew attention to an area where coordination is sorely lacking , yet desperately needed . "]
    align_list = ["0-0 1-1 2-1 1-2 2-3 4-4 3-5 5-6",
        "0-0 1-1 2-2 3-3 4-4 5-5 7-6 8-7 10-8 9-9 9-10 11-11 14-12 15-12 16-13 16-14 16-15 19-16 20-17 21-17 21-18 23-19 24-19 25-19 22-20 24-20 25-21 26-22 28-23 29-23 28-24 30-25 31-26 32-27 33-28 33-29 33-30",
        "0-2 1-3 2-4 3-4 4-4 3-5 4-6 5-7 6-8 8-9 10-10 11-11 14-12 15-12 16-12 17-12 14-13 14-14 14-15 21-16 12-17 22-21 23-21 24-21 24-22 25-24 27-25 26-26 28-26 29-27 30-28",
        "0-0 1-1 2-2 3-3 9-9 16-10 17-11 17-12 18-13 19-14 10-15 12-17 12-18 13-19 14-20 15-21 16-22 17-23 17-24 20-25 21-26 22-27 23-27 24-28",
        "0-0 1-1 2-2 3-3 4-4 5-5 6-5 7-6 13-7 8-10 9-11 10-12 11-13 12-13 12-14 16-15 15-16 19-17 25-18 25-19 26-20 27-21"]
    check_list = [('( applaudissements du groupe PSE )', '( applause from the PSE Group )'),
        ('!', 'at that .'),
        ('! nous l&apos;', 'we'),
        ('! &quot;', 'chapeau &quot;'),
        ('cruel', 'sorely')]

    max_length = 7
    for i in xrange(4, 5):
        result = test_phrase_extraction(align_list[i], l1_list[i], l2_list[i],
            check_list[i], max_length)
        print result[0]
        print result[1]
        print result[2]

def test_phrase_extraction(str_align, l1, l2, check, max_length):
    l1_words = l1.strip().split()
    l2_words = l2.strip().split()
    l1_length = len(l1_words)
    l2_length = len(l2_words)

    align = str_to_alignments(str_align)
    phrase_alignments = extract_alignments(set(align), l1_length,
        l2_length, max_length)

    phrase_pairs = set(extract_phrase_pairs_gen(phrase_alignments, l1_words,
        l2_words))

    unaligned, unaligned2 = unaligned_words(align, l1_length, l2_length)
    unaligned.extend(unaligned2)
    unaligned_pairs = list(unaligned_phrase_pairs_gen(unaligned, l1_words,
        l2_words))

    return phrase_pairs, check in phrase_pairs, unaligned_pairs


if __name__ == '__main__':
    main()
    #test()
