#!/usr/bin/env python3

import argparse
import sys
import re
import os
__version__ = '1.0.3'
__author__ = 'Joff Thyer'


class PowerStrip():

    functions = {}

    def __init__(self, filename, stutter=False):
        self.filename = filename
        self.stutter = stutter
        try:
            rootname, ext = os.path.basename(filename).split('.')
        except Exception as e:
            print('{}: ps1 extension?'.format(e))
            sys.exit(1)
        self.outputfile = '{}-stripped.{}'.format(rootname, ext)
        self.run()

    def run(self):
        print('[*] Reading Input file: {}'.format(self.filename))
        infile = open(self.filename, 'rt')
        self.contents = infile.readlines()
        infile.close()
        self.process_file()
        print('[*] Writing Output file: {}'.format(self.outputfile))
        outfile = open(self.outputfile, 'wt')
        outfile.writelines(self.results)
        outfile.close()

    def process_file(self):
        self.results = []
        skip = False
        rxp = re.compile(r'function\s([A-Za-z]+-[A-Za-z]+)')
        for line in self.contents:
            if self.stutter:
                m = rxp.match(line)
                if m:
                    self.functions[m.group(1)] = True
            if '<#' in line:
                skip = True
                continue
            elif '#>' in line:
                skip = False
                continue
            elif re.match(r'^\s*#.*$', line):
                continue
            if not skip:
                self.results.append(line)

        print('[*] {} lines in original script.'.format(len(self.contents)))
        print('[*] {} lines in new script.'.format(len(self.results)))
        print('[*] {} total lines removed.'.format(len(self.contents) - len(self.results)))

        if not self.stutter:
            return

        print('[*] Detected Function Names:')
        out = ''
        for f in sorted(self.functions.keys()):
            out += '{}, '.format(f)
            if len(out) > 60:
                print('    [+] {}'.format(out))
                out = ''
        if len(out) < 60:
            print('    [+] {}'.format(out[:-2]))
        # fix function names
        replaced = 0
        for i, line in enumerate(self.results):
            for f in self.functions:
                if f in line:
                    stutterresult = ''
                    for l in f:
                        stutterresult = stutterresult +l*2
                    self.results[i] = line.replace(f, stutterresult)
                    replaced += 1
        print('[*] {} total function names detected.'.format(len(self.functions)))
        print('[*] {} function name substitutions.'.format(replaced))

if __name__ == '__main__':
    progname = os.path.basename(sys.argv[0]).split('.')[0].title()
    banner = '''\
[*] --------------------------------------------
[*]   {}, Version: {}
[*]   Author: {}, (c) 2020
[*] --------------------------------------------
'''.format(progname, __version__, __author__)
    print(banner)
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument(
        '-s', '--stutter', default=False, action='store_true',
        help='''\
Modify function names by adding additional letter at beginning.
"Invoke-Fun" becomes "IInvoke-Fun" for example.'''
    )
    args = parser.parse_args()
    ps = PowerStrip(args.filename, args.stutter)
