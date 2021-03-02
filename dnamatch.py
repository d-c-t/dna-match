# -*- coding: utf-8 -*-
import argparse
import numpy as np
import queue
import re
import os

complement_table = {'A':'T', 'T':'A', 'C':'G', 'G':'C', 'R':'Y', 'Y':'R', 'K':'M', 'B':'V', 'D':'H'}

replacement_table = {'R':['A', 'G'], 'Y':['C', 'T'], 'S':['G', 'C'], 'W':['A', 'T'], 'K':['G', 'T'], 'M':['A', 'C'], 
                     'B':['C', 'G', 'T'], 'D':['A', 'G', 'T'], 'H':['A', 'C', 'T'], 'V':['A', 'C', 'G'], 'N':['A', 'C', 'G', 'T']}

class TreeNode:
    def __init__(self, value, arr, i, parent): #i => depth (rename when you open this in an ide)
        self.parent = parent
        children = []
        
        if i+1 == len(arr): #this is a leaf
            self.value = value
            self.children = [] # None ? we leave it as an empty list so iterating through is a lot easier
            self.is_leaf = True
            return
        
        self.is_leaf = False
        for subelem in arr[i+1]:
            subelem = TreeNode(subelem, arr, i+1, self)
            children.append(subelem)
        self.value = value
        self.children = children

def basic_complement(sequence):
    new_sequence = []
    for i,c in enumerate(sequence):
        new_sequence.append(complement_table.get(c, c))
    return ''.join([str(elem) for elem in new_sequence]) 

def create_sequence_dict(sequence):
    permutations = dict()
    permutations['base'] = sequence
    permutations['inv'] = sequence[::-1]
    permutations['comp'] = basic_complement(permutations['base'])
    permutations['inv-comp'] = basic_complement(permutations['inv'])
    return permutations                

def get_all_sublists(list_with_lists): 
    tree = TreeNode('', list_with_lists, -1, None)
    q = queue.Queue()
    q.put(tree)
    
    while not q.empty():
        elem = q.get()
        if elem.is_leaf:
            q.put(elem)
            break
        for node in elem.children:
            q.put(node)
    
    lists = []
    print('Generated {} examples'.format(q.qsize()))
    #for _ in tqdm(range(q.qsize())):
    while not q.empty():
        l = []
        elem = q.get()
        while elem.parent is not None:
            l.append(elem.value)
            elem = elem.parent
        l.append(elem.value)
        lists.append(''.join(l)[::-1])
    return lists

def perform_replacements_on_all_permutations(permutations):
    res = dict()
    for i, permutation_name in enumerate(permutations):               #'base', 'inv', 'comp', 'inv-comp' 
        print('Permutation {} of {}'.format(i+1, len(permutations)))
        arr = []
        permutation = permutations[permutation_name]    #'ARAY', 'YARA' etc
        for c in permutation:                           #'A', 'R', 'A', 'Y', etc
            replacement = replacement_table.get(c, c)   
            arr.append(replacement)                     #A,[C,T],A,[A,G]
        res[permutation_name] = get_all_sublists(arr)
    print('\n')
    return res
        
            
def start(args):
    all_bases = {}
    with open(args.input_file) as fp:
        seq = fp.readline()
        while seq:
            space = seq.index(' ')
            name = seq[0:space]
            sequence = seq[space+1:len(seq)]

            seq = sequence.strip()
            permutations = create_sequence_dict(seq)
            permutations = perform_replacements_on_all_permutations(permutations)
            all_bases[name] = permutations
            seq = fp.readline()
    
    for file in os.listdir('.'):
        if file.endswith(".fas"):
            with open(file) as fp:
                identifier = fp.readline()
                file_text = ''.join(fp.readlines()).replace('\n', '')
                finds_in_file = []
                for sequence_name in all_bases:
                    base_to_find = all_bases[sequence_name]
                    for permutation_name in base_to_find:
                        for replaced_perm in base_to_find[permutation_name]:
                            result = re.finditer(replaced_perm, file_text)
                            for res in result:
                                start = res.start()
                                end = res.end()
                                if start != end:
                                    finds_in_file.append((sequence_name, permutation_name, start, end, file_text[start:end]))
                            
                if len(finds_in_file) == 0:
                    print('WARNING: NO MATCHES IN {}!'.format(identifier))
                elif len(finds_in_file) == 1:
                    print('WARNING: ONLY 1 MATCH')
                    
                for find in finds_in_file:
                    print(find)
                if len(finds_in_file) > 0:
                    print('... in {}'.format(identifier))

    if args.verbose:
        print('\n')
        print(all_bases)


def main():
    parser = argparse.ArgumentParser(description='')
    
    parser.add_argument('-i', dest='input_file', help='input file', required=True)
    parser.add_argument('--verbose', dest='verbose', help='should print everything', required=False, default=False, action='store_true')

    options = parser.parse_args()
    start(options)


if __name__ == "__main__":
    main()