"""
CF Helper

"""

import argparse
import http.cookiejar as cookielib
import os
import random
import re
import requests
import subprocess
import sys
import time
import timeit
import yaml

from bs4 import BeautifulSoup
from lxml import html


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
    
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def print_in_color(color):
    cmd = {'red':'\033[91m', 'green':'\033[92m', 'cyan':'\033[96m'}
    def print_func(*args, **kwargs):
        for arg in args:
            print(cmd[color], arg, '\033[0m ', sep='', end='')
        print(**kwargs)
    return print_func


def error(msg, exit=True):
    red('Error:', msg)
    if exit:
        sys.exit(0)


def yes_no(msg, allow_enter=True) -> bool:
    while True:
        print(msg)
        res = input().lower()
        if res == 'y' or (allow_enter and len(res.strip())==0):
            return True
        elif res == 'n':
            return False


def process_cookies() -> cookielib.CookieJar:
    """
    Extract and return cookies of codeforces.com and atcoder.jp

    """
    cookies_path = settings['cookies_path']
    extracted = None

    try:
        cookies = cookielib.MozillaCookieJar(cookies_path)
        cookies.load()
    except FileNotFoundError:
        red(f'FileNotFound: Make sure cookies are saved at {cookies_path}')
    else:
        sites = ['codeforces.com', 'atcoder.jp']
        available = 0
        # Check how many cookies are available
        for site in sites:
            try:
                cookies._cookies[site]
            except:
                error(f'Cookies for {site} not found.', exit=False)
            else:
                available += 1
        # If no cookies available, return None
        if available == 0:
            return None
        
        extracted = cookielib.CookieJar()
        for cookie in cookies:
            for site in sites:
                if cookie.domain.find(site) != -1:
                    extracted.set_cookie(cookie)
    return extracted


def createCFArgParser() -> argparse.ArgumentParser:
    """
    Returs an argparser which parses arguments like:
        cf -g 1242
        cf -parse 333c
        cf -p https://codeforces.com/contest/143/problem/C
        cf -t c
        cf -run a
        cf -c c
        cf -a f1
    
    """
    parser = argparse.ArgumentParser(description='CF Helper Tool')

    parser.add_argument('problem', help='Problem link/id')
    parser.add_argument('-g', '-gen',
                        dest='gen', action='store_true',
                        help='Generate source code and parse IO')
    parser.add_argument('-p', '-parse', '--parse',
                        dest='parse', action='store_true',
                        help='Parse IO for the problem')
    parser.add_argument('-m', '-make', '--make',
                        dest='create', action='store_true',
                        help='Creates a dir with code files')
    parser.add_argument('-a', '-add', '--add',
                        dest='add', action='store_true',
                        help='Add more IO to probelm')
    # parser.add_argument('-t', '-test', '--test',
    #                     dest='test', action='store_true',
    #                     help='Tests the problem on sample IO')
    parser.add_argument('-r', '-run', '--run',
                        dest='run', action='store_true',
                        help='Runs the problem code, and allows you to give input')
    parser.add_argument('-j', '-java', '--java',
                        dest='java', action='store_true',
                        help='Test or run java code')
    parser.add_argument('-c', '-cpp', '--cpp',
                        dest='cpp', action='store_true',
                        help='Test or run cpp code')
    parser.add_argument('-d', '-debug', '--debug',
                        dest='debug', action='store_true',
                        help='Test/run cpp code in debug mode')
    return parser


def set_args(key, value):
    """
    Set 'key' property on args object
    """
    d = vars(args)
    d[key] = value


def run_code(compile_cmd, exec_cmd):
    cyan('Compiling', compile_cmd[-1].split("/")[-1], end='')
    try:
        subprocess.run(
            compile_cmd,
            stdout=sys.stdout,
            stderr=sys.stdout,
            bufsize=1,
            universal_newlines=True,
            check=True)
    except:
        return
    cyan('Executing code. Enter input...')
    subprocess.run(
        exec_cmd,
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stdout,
        bufsize=1,
        universal_newlines=True)


def test_code(pid, compile_cmd, exec_cmd):
    cyan('Compiling', compile_cmd[-1].split("/")[-1], end='')
    try:
        subprocess.run(
            compile_cmd,
            stdout=sys.stdout,
            stderr=sys.stdout,
            bufsize=1,
            universal_newlines=True,
            check=True)
    except:
        return

    cyan('Executing code...')
    dirpath = f'{cwd}/{pid}/io'
    if not os.path.exists(dirpath):
        error('Error: No IO directory found.')
    
    io_count = int(len(os.listdir(dirpath))/2)
    if io_count == 0:
        red('Error: No IO files found.')
        return
    for i in range(1, io_count+1):
        ifile = f'{dirpath}/in{str(i)}.txt'
        ofile = f'{dirpath}/out{str(i)}.txt'

        if (not os.path.exists(ifile)) or (not os.path.exists(ofile)):
            red("Error: INPUT/OUTPUT files don't exist.")
            continue
        
        start = timeit.default_timer()
        cp = subprocess.run(
            exec_cmd,
            stdin=open(ifile, 'r'),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True)
        stop = timeit.default_timer()
        
        stdout = cp.stdout
        expected = ''
        input_ = ''
        with open(ofile, 'r') as f:
            expected = str(f.read())
        with open(ifile, 'r') as f:
            input_ = str(f.read())
        
        verdict = True
        line = -1
        s = stdout.strip().split('\n')
        e = expected.strip().split('\n')
        if len(s) != len(e):
            verdict = False
            line = 'Number of lines not same'
        else:
            i = 1
            for x, y in zip(s, e):
                if x.strip() != y.strip():
                    verdict = False
                    line = 'Line: '+str(i)
                    break
                i += 1
        
        div = "------------------------"
        print('In/out:')
        print(input_.strip())
        print('---')
        print(stdout.strip())
        print(div)
        print('Expected:')
        print(expected.strip())
        if verdict:
            green('OK', end=' ')
            print("({0:.2f}s)".format(stop-start))
        else:
            red('Wrong Answer WA')
            print(line+" "+"({0:.2f}s)".format(stop-start))
        print(div)
        print(div)


def run(test=False):
    pid = args.problem
    if not os.path.exists(f'{cwd}/{pid}'):
        error('Please enter correct problem id.')
    
    ext = 'java' if args.java else 'cpp'
    path = f'{cwd}/{pid}/{pid}.{ext}'

    if args.java:
        classpath = f'{cwd}/{pid}'
        if test:
            test_code(pid, ['javac', path], ['java', '-cp', classpath, pid])
        else:
            run_code(['javac', path], ['java', '-cp', classpath, pid])
    
    else: # cpp
        executable_path = f'{cwd}/{pid}/{pid}.out'
        cmd = ['g++', settings['cpp']['version']]
        if args.debug:
            cmd.extend(settings['cpp']['debug'])
        else:
            cmd.extend(settings['cpp']['normal'])
        cmd.extend(['-o', executable_path, path])

        if args.debug: cyan([' '.join(cmd)])
        if test:
            test_code(pid, cmd, [executable_path])
        else:
            run_code(pid, cmd, [executable_path])


def parse_atcoder_problem_page(soup: BeautifulSoup):
    pres = soup.find_all('pre')
    ins = []
    outs = []
    c = 0
    i = 0
    while i < len(pres):
        if pres[i].var != None:
            while pres[i].var != None:
                i += 1
            c += 1
            if c == 2:
                break
            continue
        txt = pres[i].text
        ins.append(txt)
        i += 1
        txt = pres[i].text
        outs.append(txt)
        i += 1
    return ins, outs


def parse_cf_problem_page(soup: BeautifulSoup):
    br_filter = lambda x: x.find('br') == -1
    get_raw = lambda x: '\n'.join(list(filter(br_filter, x)))

    io = soup.find("div", class_="sample-test")
    if io is None:
        return [], []
    inputs = io.find_all("div", class_="input")
    outputs = io.find_all("div", class_="output")

    raw_inputs = [get_raw(e.pre.contents)+'\n' for e in inputs]
    raw_outputs = [get_raw(e.pre.contents)+'\n' for e in outputs]
    return raw_inputs, raw_outputs


def parse_problem(link, dirpath):
    page = requests.get(link, cookies=cookies)
    soup = BeautifulSoup(page.text, features="lxml")
    
    if args.cf:
        inputs, outputs = parse_cf_problem_page(soup)
    else:
        inputs, outputs = parse_atcoder_problem_page(soup)
    
    if len(inputs) == 0 or len(outputs) == 0:
        error('No IO found.', exit=False)
        return
    
    if os.path.exists(dirpath): os.system(f'rm -r {dirpath}')
    os.makedirs(dirpath)
    
    i = 1
    for x, y in zip(inputs, outputs):
        ifilename = f'{dirpath}/in{str(i)}.txt'
        ofilename = f'{dirpath}/out{str(i)}.txt'
        with open(ifilename, 'w') as f:
            f.write(x)
        with open(ofilename, 'w') as f:
            f.write(y)
        i += 1


def create_code(templatefilepath, problem_id, filepath, ptag):
    with open(templatefilepath, 'r') as template:
        code = str(template.read())
        code = code.replace("$class$", problem_id)
        code = code.replace("$problem$", ptag)

        create = True
        if os.path.exists(filepath):
            res = yes_no(f'Remove {filepath}? (y/n):')
            if res:
                os.system(f'rm {filepath}')
            else:
                create = False
        if create:
            print("Creating", filepath.split('/')[-1])
            with open(filepath, 'w') as f:
                f.write(code)


def generate_code(problem_id, ptag):
    problem_id = problem_id.lower()

    if not os.path.exists(cwd+"/"+problem_id+"/"):
        os.makedirs(cwd+"/"+problem_id+"/")
    
    for lang in settings['languages']:
        create_code(settings[lang]['template_path'],
                    problem_id,
                    f'{cwd}/{problem_id}/{problem_id}.{lang}',
                    ptag)


def gen(parse=True, code=True):
    if args.is_problem:
        pid = args.pid
        print('Parsing problem:', args.link)
        if parse:
            parse_problem(args.link, f'{cwd}/{pid.lower()}/io')
        if code:
            generate_code(pid, f'{args.tag}/{args.cid}/{args.pid}')
    
    else: # parse whole contest
        print('Parsing contest:', args.link)
        page = requests.get(args.link, cookies=cookies)
        soup = BeautifulSoup(page.text, features='lxml')

        if args.cf:
            table = soup.find_all("table", class_="problems")
            trs = table[0].find_all('tr')
        else:
            table = soup.find_all("table", class_="table")
            trs = table[0].tbody.find_all('tr')
        
        for tr in trs:
            td = tr.find_all('td')
            if len(td) == 0: continue
            
            td = td[0]
            pid = td.a.get_text().strip()
            if len(pid) == 0: continue
            problem_link = tr.a['href'].strip()
            problem_link = args.domain + problem_link
            if parse:
                parse_problem(problem_link, f'{cwd}/{pid.lower()}/io')
            if code:
                generate_code(pid, f'{args.tag}/{args.cid}/{pid}')


def create():
    generate_code(args.problem, args.problem)


def add_io():
    pid = args.problem
    if not os.path.exists(f'{cwd}/{pid}'):
        error('Please enter correct problem id.')
    
    pid = pid.lower()
    dirpath = f'{cwd}/{pid}/io/'

    if not os.path.exists(dirpath): os.makedirs(dirpath)
    
    i = int(len(os.listdir(dirpath))/2) + 1

    ifile = f'{dirpath}/in{str(i)}.txt'
    ofile = f'{dirpath}/out{str(i)}.txt'

    print('Enter input:')
    lineswrote = 0
    with open(ifile, 'w') as f:
        while True:
            x = input().strip()
            if len(x) == 0:
                break
            f.write(x+"\n")
            lineswrote += 1
    if lineswrote == 0:
        os.system('rm '+ifile)
        return
    print('Enter output:')
    with open(ofile, 'w') as f:
        while True:
            x = input().strip()
            if len(x) == 0:
                break
            f.write(x+"\n")


def parse_contest_problem():
    """
    Parses problem id passed as argument, and sets relavent properties on args object

    atcoder: https://atcoder.jp/contests/dp/tasks/dp_a
    codeforces: http://codeforces.com/contest/134/problem/D
    """
    atcoder_problem_re = '^http[s]?://atcoder\.jp/contests/(.+)/tasks/(.+)$'
    atcoder_contest_re = '^http[s]?://atcoder\.jp/contests/(.+)/tasks$'
    cf_problem_re = '^http[s]?://codeforces\.com/contest/(.+)/problem/(.+)$'
    cf_contest_re = '^http[s]?://codeforces\.com/contest/(.+)$'
    cf_gym_contest_re = '^http[s]?://codeforces\.com/gym/(.+)$'
    
    problem = args.problem
    is_link = problem.find('http') != -1
    atcoder = False
    cf = False
    is_problem = False
    is_contest = False
    pid = None
    cid = None
    if is_link:
        # error('Links not supported for now :(')
        if problem.endswith('/'): problem = problem[:-1]
        is_contest = True
        atc_match = re.search(atcoder_contest_re, problem)
        cf_match = re.search(cf_contest_re, problem)
        gym_match = re.search(cf_gym_contest_re, problem)

        if atc_match:
            atcoder = True
            cid = atc_match.group(1)
        elif cf_match:
            cf = True
            cid = cf_match.group(1)
        elif gym_match:
            cf = True
            cid = gym_match.group(1)
        else:
            error('Links are only supported contests :(')
    else:
        if problem.startswith('abc') or problem.startswith('agc'):
            atcoder = True
            tokens = problem.split('_')
            cid = tokens[0]
            if problem.find('_') != -1:
                is_problem = True
                problem = f'https://atcoder.jp/contests/{cid}/tasks/{problem}'
                pid = tokens[1]
            else:
                is_contest = True
                problem = f'https://atcoder.jp/contests/{cid}/tasks'
        else:
            cf = True
            cf_re = '^(\d+)(\w\d?)$'
            match = re.match(cf_re, problem)
            isnum = re.match('^\d+$', problem)
            if isnum:
                cid = problem
                problem = f'https://codeforces.com/contest/{cid}'
                is_contest = True
            elif match:
                cid = match.group(1)
                pid = match.group(2)
                is_problem = True
                problem = f'https://codeforces.com/contest/{cid}/problem/{pid}'
            else:
                error('Supports only AtCoder abc/agc contests and all CF contests')
    set_args('link', problem)
    set_args('atcoder', atcoder)
    set_args('cf', cf)
    set_args('is_problem', is_problem)
    set_args('is_contest', is_contest)
    set_args('pid', pid)
    set_args('cid', cid)
    set_args('tag', 'cf' if cf else 'atc')
    set_args('domain', 'https://codeforces.com' if cf else 'https://atcoder.jp')
    

if __name__ == '__main__':
    red = print_in_color('red')
    green = print_in_color('green')
    cyan = print_in_color('cyan')

    cwd = os.getcwd()
    if cwd.endswith('/'):
        cwd = cwd[:-1]
    
    settings_file = 'settings.yaml'
    settings_file = resource_path(settings_file)
    with open(settings_file, 'r') as f:
        settings = yaml.load(f, Loader=yaml.SafeLoader)
    
    if settings['force_cf_dir'] and (not cwd.endswith('cf')):
        error('This is not a "cf" directory.'
        + '\n       Can only run in directories with name ending in "cf".')
    
    cookies = process_cookies()
    parser = createCFArgParser()
    args = parser.parse_args()
    
    if args.debug and (not args.cpp):
        error('Wrong option useage: -d can only be used with -c')
    
    if args.parse or args.gen:
        parse_contest_problem()
    
    if args.run: set_args('test', False)
    else: set_args('test', True)

    if args.add: add_io()
    elif args.parse: gen(code=False)
    elif args.gen: gen()
    elif args.create: create()
    elif args.java or args.cpp:
        if args.run: run()
        else: run(test=True)
    else:
        error('Wrong option useage.')
