import queue


complement_table = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'R': 'Y', 'Y': 'R', 'K': 'M', 'B': 'V', 'D': 'H'}

replacement_table = {'R': ['A', 'G'], 'Y': ['C', 'T'], 'S': ['G', 'C'], 'W': ['A', 'T'], 'K': ['G', 'T'],
                     'M': ['A', 'C'],
                     'B': ['C', 'G', 'T'], 'D': ['A', 'G', 'T'], 'H': ['A', 'C', 'T'], 'V': ['A', 'C', 'G'],
                     'N': ['A', 'C', 'G', 'T']}


class TreeNode:
    def __init__(self, value, arr, i, parent):  # i => depth (rename when you open this in an ide)
        self.parent = parent
        children = []

        if i + 1 == len(arr):  # this is a leaf
            self.value = value
            self.children = []  # None ? we leave it as an empty list so iterating through is a lot easier
            self.is_leaf = True
            return

        self.is_leaf = False
        for subelem in arr[i + 1]:
            subelem = TreeNode(subelem, arr, i + 1, self)
            children.append(subelem)
        self.value = value
        self.children = children


def basic_complement(sequence):  # AANC -> TTNG
    new_sequence = []
    for i, c in enumerate(sequence):
        new_sequence.append(complement_table.get(c, c))
    return ''.join([str(elem) for elem in new_sequence])


def create_sequence_dict(sequence):
    permutations = dict()
    permutations['base'] = sequence
    permutations['inv'] = sequence[::-1]
    permutations['comp'] = basic_complement(permutations['base'])
    permutations['inv-comp'] = basic_complement(permutations['inv'])
    return permutations


def bfs_until_last(q):
    while not q.empty():
        elem = q.get()
        if elem.is_leaf:
            q.put(elem)
            break
        for node in elem.children:
            q.put(node)


def get_all_sublists(list_with_lists):
    tree = TreeNode('', list_with_lists, -1, None)
    q = queue.Queue()
    q.put(tree)

    bfs_until_last(q)
    print('Generated {} examples'.format(q.qsize()))

    lists = []
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
    for i, permutation_name in enumerate(permutations):  # 'base', 'inv', 'comp', 'inv-comp'
        print('Permutation {} of {}'.format(i + 1, len(permutations)))
        arr = []
        permutation = permutations[permutation_name]  # 'ARAY', 'YARA' etc
        for c in permutation:  # 'A', 'R', 'A', 'Y', etc
            replacement = replacement_table.get(c, c)
            arr.append(replacement)  # A,[C,T],A,[A,G]
        res[permutation_name] = get_all_sublists(arr)
    print('\n')
    return res


def get_permutations_of_bases(args):
    all_bases = {}
    with open(args.input_file) as fp:
        seq = fp.readline()
        if seq == '\n':     #to support adding empty newlines in the input files
            return all_bases

        while seq:
            space = seq.index(' ')
            name = seq[0:space]
            sequence = seq[space + 1:len(seq)]

            seq = sequence.strip()
            permutations = create_sequence_dict(seq)
            permutations = perform_replacements_on_all_permutations(permutations)
            all_bases[name] = permutations
            seq = fp.readline()
    return all_bases
