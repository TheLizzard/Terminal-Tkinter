import threading
import subprocess, platform
import sys, tty, termios


DEFAULT_SIZE = (80, 24)
PLATFORM = platform.system()
IS_WINDOWS = PLATFORM == "Windows"
USE_COLOUR = False
STDIN = sys.stdin
STDERR = sys.stderr

BELL_RING = "\a"
BACKSPACE = "\b"
RESET = "\u001b[0m"
BOLD = "\u001b[1m"
BLINK = "\x1b[5m"
UNDERLINED = "\u001b[4m"
REVERSED = "\u001b[7m"
CURSOR_UP = "\u001b[%dA"
CURSOR_DOWN = "\u001b[%dB"
CURSOR_RIGHT = "\u001b[%dC"
CURSOR_LEFT = "\u001b[%dD"

#Foregrounds
RED_FG = "\u001b[31m"
BLACK_FG = "\u001b[30m"
GREEN_FG = "\u001b[32m"
YELLOW_FG = "\u001b[33m"
BLUE_FG = "\u001b[34m"
MAGENTA_FG = "\u001b[35m"
CYAN_FG = "\u001b[36m"
WHITE_FG = "\u001b[37m"

B_BLACK_FG = "\u001b[30;1m"
B_RED_FG = "\u001b[31;1m"
B_GREEN_FG = "\u001b[32;1m"
B_YELLOW_FG = "\u001b[33;1m"
B_BLUE_FG = "\u001b[34;1m"
B_MAGENTA_FG = "\u001b[35;1m"
B_CYAN_FG = "\u001b[36;1m"
B_WHITE_FG = "\u001b[37;1m"

#Blackgrounds:
BLACK_BG = "\u001b[40m"
RED_BG = "\u001b[41m"
GREEN_BG = "\u001b[42m"
YELLOW_BG = "\u001b[43m"
BLUE_BG = "\u001b[44m"
MAGENTA_BG = "\u001b[45m"
CYAN_BG = "\u001b[46m"

WHITE_BG = "\u001b[47m"
B_BLACK_BG = "\u001b[40;1m"
B_RED_BG = "\u001b[41;1m"
B_GREEN_BG = "\u001b[42;1m"
B_YELLLOW_BG = "\u001b[43;1m"
B_BLUE_BG = "\u001b[44;1m"
B_MAGENTA_BG = "\u001b[45;1m"
B_CYAN_BG = "\u001b[46;1m"
B_WHITE_BG = "\u001b[47;1m"


MODIFIERS = ("\a", "\b", "\u001b[0m", "\u001b[1m", "\u001b[4m", "\u001b[7m",
             "\u001b[31m", "\u001b[45;1m", "\u001b[46;1m", "\u001b[47;1m",
             "\u001b[30m", "\u001b[32m", "\u001b[33m", "\u001b[34m",
             "\u001b[35m", "\u001b[36m", "\u001b[37m", "\u001b[30;1m",
             "\u001b[31;1m", "\u001b[32;1m", "\u001b[33;1m", "\u001b[34;1m",
             "\u001b[35;1m", "\u001b[36;1m", "\u001b[37;1m", "\u001b[40m",
             "\u001b[41m", "\u001b[42m", "\u001b[43m", "\u001b[44m",
             "\u001b[45m", "\u001b[46m", "\u001b[47m", "\u001b[40;1m",
             "\u001b[41;1m", "\u001b[42;1m", "\u001b[43;1m", "\u001b[44;1m")

MODIFIERS_DICT = {"RED_FG": "\u001b[31m", "BLACK_FG": "\u001b[30m",
                  "GREEN_FG": "\u001b[32m", "YELLOW_FG": "\u001b[33m",
                  "BLUE_FG": "\u001b[34m", "MAGENTA_FG": "\u001b[35m",
                  "CYAN_FG": "\u001b[36m", "WHITE_FG": "\u001b[37m",
                  "B_BLACK_FG": "\u001b[30;1m", "B_RED_FG": "\u001b[31;1m",
                  "B_GREEN_FG": "\u001b[32;1m", "B_YELLOW_FG": "\u001b[33;1m",
                  "B_BLUE_FG": "\u001b[34;1m", "B_MAGENTA_FG": "\u001b[35;1m",
                  "B_CYAN_FG": "\u001b[36;1m", "B_WHITE_FG": "\u001b[37;1m",
                  "BLACK_BG": "\u001b[40m", "RED_BG": "\u001b[41m",
                  "GREEN_BG": "\u001b[42m", "YELLOW_BG": "\u001b[43m",
                  "BLUE_BG": "\u001b[44m", "MAGENTA_BG": "\u001b[45m",
                  "CYAN_BG": "\u001b[46m", "WHITE_BG": "\u001b[47m",
                  "B_BLACK_BG": "\u001b[40;1m", "B_RED_BG": "\u001b[41;1m",
                  "B_GREEN_BG": "\u001b[42;1m", "B_YELLLOW_BG": "\u001b[43;1m",
                  "B_BLUE_BG": "\u001b[44;1m", "B_MAGENTA_BG": "\u001b[45;1m",
                  "B_CYAN_BG": "\u001b[46;1m", "B_WHITE_BG": "\u001b[47;1m"}


def colours_only(colours):
    output = ""
    for colour, _ in colours:
        output += colour
    return output


def colour_to_code(colour, fg=True):
    if (colour is None) or (colour == ""):
        return "", ""

    search_space = list(MODIFIERS_DICT.keys())

    search_space_copy = list(search_space)
    for key in search_space_copy:
        if ("light" in colour.lower()) and (key[:2] != "B_"):
            search_space.remove(key)
        elif ("light" not in colour.lower()) and (key[:2] == "B_"):
            search_space.remove(key)

        elif (fg is not None) and fg and (key[-3:] != "_FG"):
                search_space.remove(key)
        elif (fg is not None) and (not fg) and (key[-3:] == "_FG"):
                search_space.remove(key)

        else:
            key_sanitised = key.replace("B_", "").replace("_FG", "")
            if key_sanitised.replace("_BG", "") not in colour.upper():
                search_space.remove(key)

    if len(search_space) == 0:
        raise ValueError("Colour \"%s\" not supported." % colour)
    elif len(search_space) > 1:
        output = []
        for i in search_space:
            output.append((MODIFIERS_DICT[search_space[0]], search_space[0]))
        return output

    return MODIFIERS_DICT[search_space[0]], search_space[0]


class OutBuffer:
    def __init__(self):
        self.data = ""

    def write(self, data):
        self.data += data

    def flush(self):
        sys.stdout.write(self.data)
        sys.stdout.flush()
        self.data = ""


STDOUT = OutBuffer()


class Shell:
    def __init__(self):
        self.binds = []
        self.stdin_fd = STDIN.fileno()
        self.old_terminal_settings = termios.tcgetattr(self.stdin_fd)
        thread = threading.Thread(target=self.input_loop)
        thread.deamon = True
        thread.start()

    def write(self):
        pass

    def listen(self, func):
        self.binds.append(func)

    def stop_listen(self, func):
        self.binds.remove(func)

    def write(self, text, modifiers=None):
        WRITING_CURSOR.write(text, modifiers)

    def clear(self):
        WRITING_CURSOR.clear()

    def get_input_char(self):
        try:
            tty.setraw(self.stdin_fd)
            char = STDIN.read(1)
        finally:
            settings = self.old_terminal_settings
            termios.tcsetattr(self.stdin_fd, termios.TCSADRAIN, settings)
        return char

    def generate_event(self, event):
        for func in self.binds:
            func(event)

    def get_modifiers(self, key):
        if key == 50:
            return "shift+"
        elif key == 51:
            return "alt+"
        elif key == 52:
            return "shift+alt+"
        elif key == 53:
            return "ctrl+"
        elif key == 54:
            return "ctrl+shift+"
        else:
            STDOUT.write("Didn't understand this key modifier: "+str(next1))
            raise

    def input_loop(self):
        while True:
            char = ord(self.get_input_char())
            if char == 3:
                break # CTRL-C
            if (31 < char < 127) or (160 < char < 55296):
                self.generate_event(chr(char))
            elif char == 9:
                self.generate_event("\t")
            elif char in (10, 13):
                self.generate_event("\n")
            elif 0 < char < 27:
                key = chr(char+96)
                self.generate_event("ctrl+"+key)
            elif char == 27:
                next = ord(sys.stdin.read(1))
                if next == 91:
                    next = ord(sys.stdin.read(1))
                    if next == 50:
                        modifiers = ""
                        has_modifiers = sys.stdin.read(1) != "~"
                        if has_modifiers:
                            chars = sys.stdin.read(2)
                            next1, next2 = map(ord, chars)
                            modifiers = self.get_modifiers(next1)
                        self.generate_event(modifiers+"insert")
                    elif next == 51:
                        modifiers = ""
                        has_modifiers = sys.stdin.read(1) != "~"
                        if has_modifiers:
                            chars = sys.stdin.read(2)
                            next1, next2 = map(ord, chars)
                            modifiers = self.get_modifiers(next1)
                        self.generate_event(modifiers+"delete")
                    elif next == 65:
                        self.generate_event("up")
                    elif next == 66:
                        self.generate_event("down")
                    elif next == 67:
                        self.generate_event("right")
                    elif next == 68:
                        self.generate_event("left")
                    elif next == 49:
                        chars = sys.stdin.read(3)
                        next1, next2, next3 = map(ord, chars)
                        if next1 == 59:
                            modifiers = self.get_modifiers(next2)
                            if next3 == 65:
                                self.generate_event(modifiers+"up")
                            elif next3 == 66:
                                self.generate_event(modifiers+"down")
                            elif next3 == 67:
                                self.generate_event(modifiers+"right")
                            elif next3 == 68:
                                self.generate_event(modifiers+"left")
            elif char == 127:
                self.generate_event("black_space")
            else:
                self.generate_event("unknown")


class WritingCursor:
    def __init__(self):
        self.position = [0, 0]

    def move_by(self, delta_x, delta_y):
        self.position[0] += delta_x
        self.position[1] += delta_y

        self.position[0] = max(self.position[0], 0)
        self.position[1] = max(self.position[1], 0)

        if delta_x > 0:
            STDOUT.write(CURSOR_RIGHT%delta_x)
        elif delta_x < 0:
            STDOUT.write(CURSOR_LEFT%(-delta_x))
        if delta_y > 0:
            STDOUT.write(CURSOR_DOWN%delta_y)
        elif delta_y < 0:
            STDOUT.write(CURSOR_UP%(-delta_y))

    def move_to(self, x, y):
        delta_x = x-self.position[0]
        delta_y = y-self.position[1]
        self.move_by(delta_x, delta_y)
        assert self.position[0] == x
        assert self.position[1] == y

    def moved_to(self, x, y):
        self.position[0] = x
        self.position[1] = y

    def clear(self):
        self.moved_to(0, 0)
        if IS_WINDOWS:
            #os.system("cls")
            subprocess.Popen("cls", shell=True).communicate() 
        else: #Linux and Mac
            STDOUT.write("\033c")

    def moved_by(self, delta_x, delta_y):
        self.position[0] += delta_x
        self.position[1] += delta_y

    def reset(self):
        self.move_to(0, 0)

    def write(self, text, min=None, max=None, modifiers=None):
        if min is None:
            min = [-1, -1]
        if max is None:
            max = [1000000, 100000]
        if modifiers is None:
            modifiers = ""

        for char in text:
            if min[1] <= self.position[1] <= max[1]:
                if min[0] <= self.position[0] <= max[0]:
                    if char == "\n":
                        STDOUT.write("\r\n")
                        self.moved_to(0, self.position[1]+1)
                    else:
                        STDOUT.write(modifiers+char+RESET)
                        self.moved_by(1, 0)

        STDOUT.write("\033[?25l")


WRITING_CURSOR = WritingCursor()

if __name__ == "__main__":
    WRITING_CURSOR.clear()

    WRITING_CURSOR.move_to(5, 1)
    WRITING_CURSOR.write("#")

    WRITING_CURSOR.move_to(4, 1)
    WRITING_CURSOR.write("#")

    WRITING_CURSOR.move_to(0, 10)
