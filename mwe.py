#!/usr/bin/env python3

import sys
import argparse
import json

#import jinja2
from delphin import tdl


def argparser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("tdlpath", metavar="LEXICON_TDL_PATH")
    argparser.add_argument("outpath", metavar="OUTPUT_PATH")
    argparser.add_argument("--counts", metavar="COUNTS_PATH", default=None)
    #argparser.add_argument("-n", default=10)
    #argparser.add_argument("--debug", action='store_true')
    return argparser


def get_lex_tokens(item):
    lexemes = []
    while item is not None:
        lexeme = item['FIRST'].supertypes[0].strip('"')
        lexemes.append(lexeme)
        item = item['REST']
    return lexemes


def process_lexicon(lexicon_file, outpath, stats=None):
    mwes = []
    missing_lex_types = []
    
    for entry in tdl.parse(lexicon_file):
        item = entry['ORTH']
        lexemes = get_lex_tokens(item)
        
        if len(lexemes) > 1:
            lex_type = entry.supertypes[0]
            mwe = {
                'identifier' : entry.identifier,
                'lexemes' : lexemes,
                'length' : len(lexemes),
                'lex_type' : lex_type,
            }

            if stats is not None:
                if lex_type in stats:
                    mwe['lt_counts'] = stats[lex_type]['counts']
                    mwe['lt_trees'] = stats[lex_type]['items']
                else:
                    mwe['lt_counts'] = None
                    mwe['lt_trees'] = None
                    missing_lex_types.append(lex_type)

            mwes.append(mwe)

        output = json.dumps(mwes)
        with open(outpath, 'w') as file:
            file.write(output)

    if len(missing_lex_types) > 0:
        missing = "\n".join(missing_lex_types)
        print("No stats were found for the following lext_types:\n{}".format(missing))

            
def main(argv=None):
    if argv is None:
        arg = argparser().parse_args()
    else:
        arg = argparser().parse_args(args=argv)

    if arg.counts is not None:
        with open(arg.counts) as file:
            type_stats = json.loads(file.read())
    else:
        type_stats = None        
        
    with open(arg.tdlpath) as file:
        process_lexicon(file, arg.outpath, stats=type_stats)

        
if __name__ == "__main__":
    sys.exit(main())
