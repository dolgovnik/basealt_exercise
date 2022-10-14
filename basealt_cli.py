import argparse
import json

from basealt import Branch

'''
CLI utility to work with Branch objects. It compares two branch objects and filters result.

Examples.
Get all archetectures for branch p10:
python3 basealt_cli.py getarchs p10

Compare packages in two branches sisyphus and p10:
python3 basealt_cli.py compare sisyphus p10


Compare packages in two branches sisyphus and p10, but show results for x86_64 and noarch archetectures
and only added and updated packages:
python3 basealt_cli.py compare sisyphus p10 -t added updated -a x86_64 noarch
'''

if __name__ == '__main__':

    # Parse CLI arguments
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

    # Get avaliable archetectures for branch
    if args.cmd == 'getarchs':
        b1 = Branch(args.branch[0])
        print('\nAvaliable archetectures are:')
        print(json.dumps(b1.archs_set, indent=4))
    # Compare packages in two branches
    elif args.cmd == 'compare':
        # If only one branch in input - show error message
        if len(args.branch) < 2:
            print('There should be two branches to compare')
        else:
            b1 = Branch(args.branch[0])
            b2 = Branch(args.branch[1])
            b1.compare(b2)
            result = b1.comparsion_result

            # If archetecture or type in input - filter result dict
            if args.arch:
                archs_to_del = result['result'].keys() - set(args.arch)
                for a in archs_to_del:
                    del result['result'][a]

            if args.type:
                for arch in result['result']:
                    types_to_del = result['result'][arch].keys() - set(args.type)
                    for a in types_to_del:
                        del result['result'][arch][a]

            # Prettyprint json result
            print(json.dumps(result, indent=4))
