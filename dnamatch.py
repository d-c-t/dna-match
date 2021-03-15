import argparse
import re
import os
import sys

from basegenerator import get_permutations_of_bases
import metrics


def find_in_file_regex(all_bases, file_text):
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
                        finds_in_file.append(
                            (sequence_name, permutation_name, start, end, file_text[start:end]))
    return finds_in_file


def find_in_file(all_bases, file_text, max_len_multiplier = 1.5):
    best_in_file = []
    for sequence_name in all_bases:
        base_to_find = all_bases[sequence_name]
        for permutation_name in base_to_find: #'base', 'inv', ...
            for replaced_perm in base_to_find[permutation_name]: #every result for the initial permutation substitution
                max_len = int(len(replaced_perm) * max_len_multiplier) + 1
                current_best = (9999999, '', '', -1, -1, '')
                for i, j in zip(range(len(file_text) - max_len), range(max_len, len(file_text) - max_len)):
                    lev_diff = metrics.levenshtein(replaced_perm, file_text[i:j])
                    if lev_diff < current_best[0]:
                        current_best = (lev_diff, sequence_name, permutation_name, i, j, file_text[i:j])
                best_in_file.append(current_best)
    return best_in_file


def start(args):
    try:
        all_bases = get_permutations_of_bases(args)
    except ValueError:
        sys.exit('ValueError when generating permutations of bases! Maybe you forgot to identify your primer?')

    for file in os.listdir(args.input_dir):
        if file.endswith(".fas"):
            with open(file) as fp:
                identifier = fp.readline()
                file_text = ''.join(fp.readlines()).replace('\n', '')
                finds_in_file = find_in_file_regex(all_bases, file_text)

                if len(finds_in_file) == 0:
                    print('WARNING: NO MATCHES IN {}! LOOKING FOR THE CLOSEST RESULT'.format(identifier))
                    #finds_in_file = find_in_file(all_bases, file_text, args.length_threshold)
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
    parser.add_argument('-input_dir', dest='input_dir', help='directory where your .fas files are located',
                        required=False, default='.')
    parser.add_argument('-lt', dest='length_threshold', help='length threshold of file chunks to look through. default should be good enough in most cases',
                        required=False, default=1.5, type=float)

    parser.add_argument('--verbose', dest='verbose', help='should print everything', required=False, default=False,
                        action='store_true')
    parser.add_argument('--todo', dest='todo', required=False, default=False, action='store_true')

    options = parser.parse_args()
    if options.todo:
        print('TODO:ADD EXACT MODE OPTIMIZED FOR REGEX')
        print('TODO:ADD SUPPORT FOR DIFF COUNT')
    start(options)


if __name__ == "__main__":
    main()
