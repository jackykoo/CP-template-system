#!/usr/bin/env python

from urllib.request import urlopen
from html.parser import HTMLParser
from subprocess import call
import os
import re
import argparse
import platform

###########################
# User modifiable constants
###########################
language_params = {
        'c++17' : {
            'TEMPLATE'    : 'template.cpp',
            'DEBUG_FLAGS' : '-DDEBUG',
            'COMPILE_CMD' : 'g++ -g -std=c++1z -Wall $DBG',
            'RUN_CMD'     : './a.out'
            },
        'go'    : {
            'TEMPLATE'    : 'main.go',
            'COMPILE_CMD' : 'go build $DBG -o a.out',
            'DEBUG_FLAGS' : '''"-ldflags '-X=main.DEBUG=Y'"''',
            'RUN_CMD'     : './a.out'
            },
        'kotlin'    : {
            'TEMPLATE'    : 'main.kt',
            'COMPILECMD' : 'kotlinc -include-runtime -d out.jar',
            'DEBUG_FLAGS' : "-d",
            'RUN_CMD'     : 'java -jar out.jar $DBG'
            },
        }

SAMPLE_INPUT='.in'
SAMPLE_OUTPUT='.out'
MY_OUTPUT='my_output'
CWD = os.getcwd()
HOME = '/Users/jackykoo'

# Do not modify these!
RED_F='\033[31m'
GREEN_F='\033[32m'
BOLD='\033[1m'
NORM='\033[0m'
if platform.system() == "Darwin":
    TIME_CMD='`which gtime` -o time.out -f "(%es)"'
else:
    TIME_CMD='`which time` -o time.out -f "(%es)"'
TIME_AP='`cat time.out`'


# Contest parser.
class CodeforcesContestParser(HTMLParser):

    def __init__(self, contest):
        HTMLParser.__init__(self)
        self.contest = contest
        self.start_contest = False
        self.start_problem = False
        self.name = ''
        self.problem_name = ''
        self.problems = []
        self.problem_names = []

    def handle_starttag(self, tag, attrs):
        if self.name == '' and attrs == [('style', 'color: black'), ('href', '/contest/%s' % (self.contest))]:
                self.start_contest = True
        elif tag == 'option':
            if len(attrs) == 1:
                regexp = re.compile(r"'[A-Z][0-9]?'") # The attrs will be something like: ('value', 'X'), or ('value', 'X1')
                string = str(attrs[0])
                search = regexp.search(string)
                if search is not None:
                    self.problems.append(search.group(0).split("'")[-2])
                    self.start_problem = True

    def handle_endtag(self, tag):
        if tag == 'a' and self.start_contest:
            self.start_contest = False
        elif self.start_problem:
            self.problem_names.append(self.problem_name)
            self.problem_name = ''
            self.start_problem = False

    def handle_data(self, data):
        if self.start_contest:
            self.name = data
        elif self.start_problem:
            self.problem_name += data


# Problems parser.
class CodeforcesProblemParser(HTMLParser):

    def __init__(self, folder):
        HTMLParser.__init__(self)
        self.folder = folder
        self.num_tests = 0
        self.testcase = None
        self.start_copy = False

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            if attrs == [('class', 'input')]:
                self.num_tests += 1
                self.testcase = open(
                    '%s/%d%s' % (self.folder, self.num_tests, SAMPLE_INPUT), 'wb')
            elif attrs == [('class', 'output')]:
                self.testcase = open(
                    '%s/%d%s' % (self.folder, self.num_tests, SAMPLE_OUTPUT), 'wb')
        elif tag == 'pre':
            if self.testcase is not None:
                self.start_copy = True

    def handle_endtag(self, tag):
        if tag == 'br':
            if self.start_copy:
                self.testcase.write('\n'.encode('utf-8'))
                self.end_line = True
        if tag == 'pre':
            if self.start_copy:
                if not self.end_line:
                    self.testcase.write('\n'.encode('utf-8'))
                self.testcase.close()
                self.testcase = None
                self.start_copy = False

    def handle_entityref(self, name):
        if self.start_copy:
            self.testcase.write(self.html.unescape(('&%s;' % name)).encode('utf-8'))

    def handle_data(self, data):
        if self.start_copy:
            self.testcase.write(data.strip('\n').encode('utf-8'))
            self.end_line = False


# Parses each problem page.
def parse_problem(folder, contest, problem):
    url = 'http://codeforces.com/contest/%s/problem/%s' % (contest, problem)
    html = urlopen(url).read()
    parser = CodeforcesProblemParser(folder)
    parser.feed(html.decode('utf-8'))
    # .encode('utf-8') Should fix special chars problems?
    return parser.num_tests

# Parses the contest page.
def parse_contest(contest):
    url = f'http://codeforces.com/contest/${contest}'
    html = urlopen(url).read()
    parser = CodeforcesContestParser(contest)
    parser.feed(html.decode('utf-8'))
    return parser


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--language', default="c++17", help="The programming language to use ")
    parser.add_argument('contest', help="The Codeforce contest number ")
    args = parser.parse_args()

    contest = args.contest
    language = args.language

    # Find contest and problems.
    print (f'Parsing contest {contest} please wait...')
    content = parse_contest(contest)
    print (BOLD+GREEN_F+'*** Round name: '+content.name+' ***'+NORM)
    print (f'Found {len(content.problems)} problems!')

    # Find problems and test cases.
    for index, problem in enumerate(content.problems):
        print (f'Downloading Problem {problem}: {content.problem_names[index]}...')
        folder = f'{CWD}/{contest}/{problem}/'
        template_path = f'{HOME}/programming/CP-template-system/template.cpp'
        makefile_path = f'{HOME}/programming/CP-template-system/Makefile'
        call(['mkdir', '-p', folder])
        call(['cp', '-n', template_path, f'{folder}/{problem}.cpp'])
        call(['cp', '-n', makefile_path, f'{folder}/Makefile'])
        num_tests = parse_problem(folder, contest, problem)
        print(f'{num_tests} sample test(s) found.')
        print ('========================================')

    print('GOOD LUCK!! \U0001F4AB')


if __name__ == '__main__':
    main()
