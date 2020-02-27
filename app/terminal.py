from termcolor import colored
from ftplib import error_perm
from ftplib import FTP
import getpass
import os
import socket


class Terminal:

    def __init__(self):
        self.login = None
        self.ftp = None
        self.is_run = True

    def run(self):
        while self.is_run:
            try:
                if not self.ftp:
                    self.auth()
                else:
                    text = colored(self.login, 'green') + colored('~' + self.ftp.pwd(), 'blue') + ': '
                    print(text, end='')
                    string = input()
                    params = string.split(' ')
                    func = self.commands(params.pop(0))
                    func(params)
            except error_perm as e:
                print(colored(e.args[0], 'red'))
            except TypeError:
                print(colored('Command not found!', 'red'))
            except IndexError:
                print(colored('Not enough params!', 'red'))
            except FileNotFoundError:
                print(colored('Invalid filename!', 'red'))
            except ConnectionAbortedError:
                self.ftp = None
                print(colored('Timeout! You were disconnected from server!', 'red'))

    def auth(self):
        ip = input('Enter FTP address: ')
        login = input('Enter your login: ')
        password = getpass.getpass('Enter your password: ')
        try:
            self.ftp = FTP(ip, user=login, passwd=password)
            self.ftp.encoding = 'utf-8'
            self.login = login
        except error_perm as e:
            print(colored(e.args[0], 'red'))
        except socket.gaierror:
            print(colored('Wrong address!', 'red'))

    def commands(self, command):
        return {'cd': self.cwd,
                'pwd': self.pwd,
                'ls': self.dir,
                'mkdir': self.make_dir,
                'rmfile': self.remove_file,
                'rmdir': self.remove_dir,
                'rename': self.rename,
                'download': self.download,
                'upload': self.upload,
                'help': self.help,
                'quit': self.quit}.get(command)

    def cwd(self, params):
        self.ftp.cwd(params[0])

    def pwd(self, params):
        print(self.ftp.pwd())

    def dir(self, params):
        self.ftp.dir()

    def make_dir(self, params):
        self.ftp.mkd(params[0])

    def remove_file(self, params):
        self.ftp.delete(params[0])

    def remove_dir(self, params):
        self.ftp.rmd(params[0])

    def rename(self, params):
        self.ftp.rename(params[0], params[1])

    def download(self, params):
        target_name = params[0].split('/')[-1] if len(params) == 1 else params[1]
        try:
            with open('client/' + target_name, 'wb') as f:
                self.ftp.retrbinary('RETR ' + params[0], f.write)
        except error_perm as e:
            if os.path.exists('client/' + target_name):
                os.remove('client/' + target_name)
            print(colored(e.args[0], 'red'))

    def upload(self, params):
        target_name = params[0].split('/')[-1] if len(params) == 1 else params[1]
        with open(params[0], 'rb') as f:
            self.ftp.storbinary('STOR ' + target_name, f, 1024)

    def quit(self, params):
        self.ftp.quit()
        self.is_run = False

    def help(self, params):
        print('cd       change current directory        [path*]\n'
              'pwd      working directory path          []\n'
              'ls       working directory files list    []\n'
              'mkdir    make new directory              [pathname*]\n'
              'rmfile   remove file                     [pathname*]\n'
              'rmdir    remove directory                [pathname*]\n'
              'rename   rename file or directory        [pathname*, new name*]\n'
              'download download file from the server   [pathname*, new name]\n'
              'upload   upload file to the server       [pathname*]\n'
              'help     shows available commands        []\n'
              'quit     disconnect from the server      []')
