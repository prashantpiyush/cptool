# cf helper

import random
import subprocess
import sys
import os
import time
import timeit
import requests
import http.cookiejar as cookielib
from bs4 import BeautifulSoup
from lxml import html

javatemplate_path = '/home/piyush/Projects/cc/1cptools/template/template.txt'
cpptemplate_path = '/home/piyush/Projects/cc/1cptools/template/templatecpp.txt'
cookies_path = '/home/piyush/Downloads/cookies.txt'
cppversion = '-std=c++17'
cppcheck_options_path = '/home/piyush/Projects/cc/1cptools/template/cppoptions'
languages_options_path = '/home/piyush/Projects/cc/1cptools/template/languages'

def red(*args, **kwargs):
    for a in args:
        print('\033[91m',a,'\033[0m', sep='', end='')
        print(' ', end='')
    print(**kwargs)

def green(*args, **kwargs):
    for a in args:
        print('\033[92m',a,'\033[0m', sep='', end='')
        print(' ', end='')
    print(**kwargs)

def cyan(*args, **kwargs):
    for a in args:
        print('\033[96m',a,'\033[0m', sep='', end='')
        print(' ', end='')
    print(**kwargs)


def parse_problem(problem_link, dir):
    page = requests.get(problem_link, cookies=cookies)
    soup = BeautifulSoup(page.text, features="lxml")

    # print(soup)
    br_filter = lambda x: x.find('br') == -1
    get_raw = lambda x: '\n'.join(list(filter(br_filter, x)))

    err_msg = 'Error: Sample input/output not found.'
    io = soup.find("div", class_="sample-test")
    if io is None:
        red(err_msg)
        return
    inputs = io.find_all("div", class_="input")
    outputs = io.find_all("div", class_="output")

    raw_inputs = [get_raw(e.pre.contents)+'\n' for e in inputs]
    raw_outputs = [get_raw(e.pre.contents)+'\n' for e in outputs]

    # print("io dir", dir, os.path.exists(dir))
    if os.path.exists(dir):
        # print('Creating dir', dir)
        os.system('rm -r '+dir)
    os.makedirs(dir)
    
    i = 1
    for x, y in zip(raw_inputs, raw_outputs):
        ifilename = dir+'/in'+str(i)+'.txt'
        ofilename = dir+'/out'+str(i)+'.txt'
        with open(ifilename, 'w') as f:
            f.write(x)
        with open(ofilename, 'w') as f:
            f.write(y)
        i += 1
    # print('Total sample inputs:',i-1)

def add_input():
    contest_id, problem_id = split_contest_problem(args[1])
    if problem_id is None:
        red('Error: Problem id is required.')
        return
    problem_id = problem_id.lower() if problem_id != 'Main' else problem_id
    dir = cwd+"/"+problem_id+"/io/"
    if not os.path.exists(dir):
        os.makedirs(dir)
    i = int(len(os.listdir(dir))/2) + 1
    ifile = dir+'/in'+str(i)+'.txt'
    ofile = dir+'/out'+str(i)+'.txt'

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

def create_code(templatefilepath, problem_id, filepath, ptag):
    with open(templatefilepath, 'r') as template:
        code = str(template.read())
        code = code.replace("$class$", problem_id)
        code = code.replace("$problem$", ptag)

        create = False
        if os.path.exists(filepath):
            while True:
                print('Remove '+filepath+'? (Y/N)')
                res = input().lower()
                if res == 'y' or len(res.strip())==0:
                    print('Removing...')
                    os.system('rm '+filepath)
                    create = True
                    break
                elif res == 'n':
                    break
        else:
            create = True
        if create:
            print("Creating", filepath.split('/')[-1])
            with open(filepath, 'w') as f:
                f.write(code)

def generate_code(problem_id, ptag, lower=True):    
    problem_id = problem_id.lower() if lower else problem_id

    if not os.path.exists(cwd+"/"+problem_id+"/"):
            os.makedirs(cwd+"/"+problem_id+"/")
    
    if java:
        create_code(javatemplate_path,
            problem_id,
            cwd+"/"+problem_id+"/"+problem_id+".java",
            ptag)
    
    if cpp:
        create_code(cpptemplate_path,
            problem_id,
            cwd+"/"+problem_id+"/"+problem_id+".cpp",
            ptag)

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


def run():
    filename = args[1]
    full = filename
    if not filename.endswith('.java'):
        full = filename + '/' + filename + '.java'
    path = cwd + '/' + full
    classpath = cwd+'/'+filename
    run_code(['javac', path], ['java', '-cp', classpath, filename])
    cleandir(cwd+'/'+filename)

def run_cpp(check=False):
    filename = args[1]
    full = filename
    if not filename.endswith('.cpp'):
        full = filename + '/' + filename + '.cpp'
    path = cwd + '/' + full
    executable_path = cwd+'/'+filename+'/'+filename+'.out'
    cmd = ['g++', cppversion]
    if check:
        cmd.extend(cppcheck_options)
    else:
        cmd.extend(['-Wshadow', '-Wall'])
    cmd.extend(['-o', executable_path, path])
    if check: cyan([' '.join(cmd)])
    run_code(
        cmd,
        [executable_path]
    )
    cleandir(cwd+'/'+filename)

def test_code(filename, compile_cmd, exec_cmd):
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
    dir = cwd+'/'+filename+'/io/'
    if not os.path.exists(dir):
        red('Error: No IO directory found.')
        return
    io_count = int(len(os.listdir(dir))/2)
    if io_count == 0:
        red('Error: No IO files found.')
        return
    for i in range(1, io_count+1):
        ifile = cwd+'/'+filename+'/io/'+'/in'+str(i)+'.txt'
        ofile = cwd+'/'+filename+'/io/'+'/out'+str(i)+'.txt'

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

def test():
    filename = args[1]
    full = filename
    if not filename.endswith('.java'):
        full = filename + '/' + filename + '.java'
    path = cwd + '/' + full
    test_code(filename, ['javac', path], ['java', '-cp', cwd+'/'+filename, filename])
    cleandir(cwd+'/'+filename)

def test_cpp(check=False):
    filename = args[1]
    full = filename
    if not filename.endswith('.cpp'):
        full = filename + '/' + filename + '.cpp'
    path = cwd + '/' + full
    executable_path = cwd+'/'+filename+'/'+filename+'.out'
    cmd = ['g++', cppversion]
    if check:
        cmd.extend(cppcheck_options)
    else:
        cmd.extend(['-Wshadow', '-Wall'])
    cmd.extend(['-o', executable_path, path])
    if check: cyan([' '.join(cmd)])
    test_code(
        filename,
        cmd,
        [executable_path]
    )
    cleandir(cwd+'/'+filename)

def cleandir(dir):
    try:
        for c in os.listdir(dir):
            if c.endswith('.class'):
                cmd = 'rm ' +dir+'/'+c.replace("$", "\$")
                os.system(cmd)
            elif c.endswith('.out'):
                cmd = 'rm ' +dir+'/'+c
                os.system(cmd)
    except NotADirectoryError:
        pass

def clean():
    for f in os.listdir(cwd):
        cleandir(cwd+'/'+f)

def cleanio():
    for f in os.listdir(cwd):
        cleandir(cwd+'/'+f)
        if os.path.exists(cwd+'/'+f+'/io'):
            os.system('rm -r '+cwd+'/'+f+'/io')

def cleanall():
    cleanio()
    for l in sorted(os.listdir(cwd)):
        while True:
            print('Remove '+l+'? (Y/N)')
            res = input().lower()
            if res == 'y' or len(res.strip())==0:
                os.system('rm -r '+cwd+'/'+l)
                break
            elif res == 'n':
                break

def split_contest_problem(s):
    for i in range(len(s)):
        c = s[i]
        if ord(c) < ord('0') or ord('9') < ord(c):
            return s[:i], s[i:]
    return s, None

def create():
    if len(args) == 1:
        generate_code('Main', 'Main/Main', lower=False)
    else:
        nm = args[1].strip()
        generate_code(nm, nm+'/'+nm, lower=False)

def gen(code=True):
    if len(args) == 1:
        generate_code('Main', lower=False)
        return
    
    contest_id, problem_id = split_contest_problem(args[1])

    if problem_id != None:
        problem_id = problem_id.upper()
        problem_link = 'https://codeforces.com/contest/' + contest_id + '/problem/' + problem_id
        print('Parsing problem', problem_link)
        parse_problem(problem_link, cwd+'/'+problem_id.lower()+'/io')
        if code:
            generate_code(problem_id, 'cf/'+contest_id+'/'+problem_id)
        sys.exit(0)
    
    # parse whole contest
    contest_url = 'https://codeforces.com/contest/' + contest_id
    print('Parsing contest', contest_url)
    page = requests.get(contest_url, cookies=cookies)
    soup = BeautifulSoup(page.text, features="lxml")

    table = soup.find_all("table", class_="problems")
    trs = table[0].find_all('tr')


    for tr in trs:
        td = tr.find_all('td')
        if len(td) == 0:
            continue
        td = td[0]
        problem_id = td.a.get_text().strip()
        problem_link = tr.a['href'].strip()
        problem_link = 'https://codeforces.com' + problem_link
        parse_problem(problem_link, cwd+'/'+problem_id.lower()+'/io')
        if code:
            generate_code(problem_id, 'cf/'+contest_id+'/'+problem_id)
        # print(problem_id, problem_link)

def gym():
    url = args[1]

    if url.find('https') == -1:
        url = 'https://codeforces.com/gym/'+url
    
    contest_id = url.split('/')[-1]
    print('Parsing contest', url)
    page = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(page.text, features="lxml")

    table = soup.find_all("table", class_="problems")
    trs = table[0].find_all('tr')

    for tr in trs:
        td = tr.find_all('td')
        if len(td) == 0:
            continue
        td = td[0]
        problem_id = td.a.get_text().strip()
        problem_link = tr.a['href'].strip()
        problem_link = 'https://codeforces.com' + problem_link
        parse_problem(problem_link, cwd+'/'+problem_id.lower()+'/io')
        generate_code(problem_id, 'cf/'+contest_id+'/'+problem_id)

def get_cpp_check_options():
    with open(cppcheck_options_path, 'r') as f:
        options = str(f.read())
        def chk(s):
            if len(s) == 0: return False
            if s.startswith('#'): return False
            if not s.startswith('-'): return False
            return True
        options = list(filter(chk, options.split('\n')))
        return options

def get_languages():
    global java, cpp
    with open(languages_options_path, 'r') as f:
        options = str(f.read())
        def chk(s):
            if len(s) == 0: return False
            if s.startswith('#'): return False
            return True
        options = list(filter(chk, options.split('\n')))
        if 'java' in options:
            java = True
        if 'cpp' in options:
            cpp = True

if __name__ == '__main__':
    args = sys.argv[1:]
    cwd = os.getcwd()
    # print('Cwd', cwd)
    if cwd[-1] == '/':
        cwd = cwd[:-1]
    if not cwd.endswith('cf'):
        red('Error: This is not an codeforces directory.')
        sys.exit(0)
    
    try:
        cookies = cookielib.MozillaCookieJar(cookies_path)
        cookies.load()
    except FileNotFoundError:
        red('Error: Load codeforces.com cookies again.')
        cookies = None
    if cookies is not None:
        # internal_cookies = cookies#._cookies
        try:
            cookies._cookies['codeforces.com']
        except KeyError:
            red('Error: Load codeforces.com cookies again.')
        cj = cookielib.CookieJar()
        for cookie in cookies:
            if cookie.domain.find('codeforces.com') != -1:
                cj.set_cookie(cookie)
                # print(cookie.name, cookie.value, cookie.domain)
        cookies = cj
    
    java = False
    cpp = False
    get_languages()
    # print('java', java, 'cpp', cpp)

    # if cwd[-1] == '/':
    #     cwd = cwd[:-1]
    if args[0] == 'run':
        run()
    elif args[0] == 'test':
        test()
    elif args[0] == 'parse':
        gen(code=False)
    elif args[0] == 'gen':
        gen()
    elif args[0] == 'create':
        create()
    elif args[0] == 'clean':
        clean()
    elif args[0] == 'cleanio':
        cleanio()
    elif args[0] == 'cleanall':
        cleanall()
    elif args[0] == 'add':
        add_input()
    elif args[0] == 'gym':
        gym()
    elif args[0] == 'java':
        option = args[1]
        if(option=='-r'):
            args[1] = args[2]
            run()
        else:
            test()
    elif args[0] == 'cpp':
        option = args[1]
        if(option=='-r'):
            args[1] = args[2]
            run_cpp()
        else:
            test_cpp()
    elif args[0] == 'cppcheck':
        option = args[1]
        cppcheck_options = get_cpp_check_options()
        if(option=='-r'):
            args[1] = args[2]
            run_cpp(check=True)
        else:
            test_cpp(check=True)
    else:
        print('Wrong arguments. Try again.')
        sys.exit(0)

    clean()