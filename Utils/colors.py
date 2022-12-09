#class colors:
PINK = '\033[95m'
BLUE = '\033[94m'
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
ENDC = '\033[0m'

def pink(text):      return (f"{PINK}{text}{ENDC}")
def blue(text):      return (f"{BLUE}{text}{ENDC}")
def cyan(text):      return (f"{CYAN}{text}{ENDC}")
def green(text):     return (f"{GREEN}{text}{ENDC}")
def yellow(text):    return (f"{YELLOW}{text}{ENDC}")
def red(text):       return (f"{RED}{text}{ENDC}")
def bold(text):      return (f"{BOLD}{text}{ENDC}")
def underline(text): return (f"{UNDERLINE}{text}{ENDC}")