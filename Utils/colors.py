class colors:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def pink(text):      return (f"{colors.PINK}{text}{colors.ENDC}")
    def blue(text):      return (f"{colors.BLUE}{text}{colors.ENDC}")
    def cyan(text):      return (f"{colors.CYAN}{text}{colors.ENDC}")
    def green(text):     return (f"{colors.GREEN}{text}{colors.ENDC}")
    def yellow(text):    return (f"{colors.YELLOW}{text}{colors.ENDC}")
    def red(text):       return (f"{colors.RED}{text}{colors.ENDC}")
    def bold(text):      return (f"{colors.BOLD}{text}{colors.ENDC}")
    def underline(text): return (f"{colors.UNDERLINE}{text}{colors.ENDC}")