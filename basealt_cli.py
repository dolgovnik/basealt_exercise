import argparse
import json

from basealt import Branch

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Comparing binary packages between two branches of Simply Linux')

    parser.add_argument('cmd', type=str, choices=['getarchs', 'compare'],
                        help='Command to be executed. Required argument.')
    parser.add_argument('branch', type=str, choices=['sisyphus', 'p10', 'p9'], nargs='+',
                        help='Branch to work with. Required argument.')
    parser.add_argument('-a', '--arch', type=str, nargs='+',
                        help='Archetecture to work with. Optional argument.')
    parser.add_argument('-t', '--type', type=str, choices=['added', 'removed', 'updated', 'suspicious'], nargs='+',
                        help='Type of package. Optional argument.')

    args = parser.parse_args()

    if args.cmd == 'getarchs':
        b1 = Branch(args.branch[0])
        print('\nAvaliable archetectures are:')
        print(json.dumps(b1.archs_set, indent=4))
    elif args.cmd == 'compare':
        if len(args.branch) < 2:
            print('There should be two branches to compare')
        else:
            b1 = Branch(args.branch[0])
            b2 = Branch(args.branch[1])
            b1.compare(b2)
            result = b1.comparsion_result

            if args.arch:
                archs_to_del = set(result['result'].keys()) - set(args.arch)
                for a in archs_to_del:
                    del result['result'][a]

            if args.type:
                for arch in result['result']:
                    types_to_del = set(result['result'][arch].keys()) - set(args.type)
                    for a in types_to_del:
                        del result['result'][arch][a]

            print(json.dumps(result, indent=4))
