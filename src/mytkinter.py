import threading
import string
import shell
import copy
import sys


STDOUT = shell.STDOUT
STDERR = shell.STDERR
STDIN = shell.STDIN


SHELL = shell.Shell()
DEFAULT_SIZE = shell.DEFAULT_SIZE
BLANK = (" "*DEFAULT_SIZE[0]+"\n")*DEFAULT_SIZE[1]


class WritingCursor:
    def __init__(self):
        self.position = shell.WRITING_CURSOR.position

    def __setitem__(self, key, value):
        self.set(*key, value)

    def clear(self):
        shell.WRITING_CURSOR.clear()

    def reset(self):
        shell.WRITING_CURSOR.reset()

    def move_by(self, delta_x, delta_y):
        shell.WRITING_CURSOR.move_by(delta_x, delta_y)

    def moved_by(self, delta_x, delta_y):
        shell.WRITING_CURSOR.moved_by(delta_x, delta_y)

    def move_to(self, x, y):
        shell.WRITING_CURSOR.move_to(x, y)

    def moved_to(self, x, y):
        shell.WRITING_CURSOR.moved_to(x, y)

    def reset(self):
        shell.WRITING_CURSOR.reset()

    def write(self, text, min=None, max=None, modifiers=None):
        shell.WRITING_CURSOR.write(text, min, max, modifiers=modifiers)

    def set(self, x, y, string, min=None, max=None, modifiers=None):
        self.move_to(x, y)
        self.write(string, min, max, modifiers)

    def draw_line(self, coord1, coord2, modifiers=None, char=None):
        x1, y1 = coord1
        x2, y2 = coord2
        if x1 == x2: # Vertical line
            if char is None:
                char = "|"
            for y in range(y1, y2):
                self.set(x1, y, char, modifiers)
        elif y1 == y2: # Horisontal line
            self.set(x1, y1, char*(x2-x1), modifiers)
        else:
            raise TclError(1)

    def draw_rectangle(self, A, D, charh="═", charv="║", corners="    ",
                       modifiers=None):
        """ A -- B
            |    |
            C -- D """
        x1, y1 = A
        x2, y2 = D
        self.draw_line((x1+1, y1), (x2-1, y1), modifiers, char=charh) # AB
        self.draw_line((x1, y1+1), (x1, y2-1), modifiers, char=charv) # AC
        self.draw_line((x2-1, y1+1), (x2-1, y2-1), modifiers, char=charv) # BD
        self.draw_line((x1+1, y2-1), (x2-1, y2-1), modifiers, char=charh) # CD
        self.set(x1, y1, corners[0], modifiers) #     A
        self.set(x2-1, y1, corners[1], modifiers) #   B
        self.set(x1, y2-1, corners[2], modifiers) #   C
        self.set(x2-1, y2-1, corners[3], modifiers) # D


WRITING_CURSOR = WritingCursor()


class Cursor:
    def __init__(self):
        self.sprite = "⬉"
        self.sprites = {"mouse_cursor": "⬉",
                        "text_cursor": "ꕯ",
                        "text_cursor2": "Ꮖ"}
        self.position = [40, 12]
        self.position = [0, 0]
        self.last_position = tuple(self.position)
        self.check_out_of_bounds()

    def change_sprite(self, sprite_name):
        self.sprite = self.sprites[sprite_name]

    def move_to(self, x, y):
        self.last_position = copy.deepcopy(self.position)
        self.move_to_no_log(x, y)

    def move_to_no_log(self, x, y):
        self.position[0] = x
        self.position[1] = y
        self.check_out_of_bounds()

    def move_by(self, delta_x, delta_y):
        self.last_position = copy.deepcopy(self.position)
        self.move_by_no_log(delta_x, delta_y)

    def move_by_no_log(self, delta_x, delta_y):
        self.position[0] += delta_x
        self.position[1] += delta_y
        self.check_out_of_bounds()

    def check_out_of_bounds(self):
        self.position[0] = max(self.position[0], 0)
        self.position[1] = max(self.position[1], 0)
        self.position[0] = min(self.position[0], DEFAULT_SIZE[0]-1)
        self.position[1] = min(self.position[1], DEFAULT_SIZE[1]-1)

    def show(self):
        WRITING_CURSOR.set(*self.position, self.sprite, modifiers=shell.RESET)


CURSOR = Cursor()


class TclError(Exception):
    def __init__(self, error, widget=None):
        self.error = error
        self.widget = widget
        self.text = self.get_text(error)
        super().__init__(self.text)

    def __repr__(self):
        return f"<TclError object at {hex(id(self))} error=\"{self.text}\">"

    def get_text(self, error):
        if error == 0:
            return f"Unregistered window {self.widget}"
        elif error == 1:
            return "Tried writing a line that isn't horisontal or vertical."
        elif error == 2:
            return "Unknown dimentions"
        elif error == 3:
            return "Tried using a destroyed object."
        elif error == 4:
            return "Tried griding an object that doesn't belong to this window."
        elif error == 5:
            return "This window/widget has been destroyed."
        elif error == 6:
            return "Can't unregister a window that hasn't been registered."
        elif error == 7:
            return "Sprite doesn't exist."
        else:
            return f"Unknown error occured"


class Screen:
    def __init__(self, size=DEFAULT_SIZE):
        SHELL.listen(self.event)
        self.windows = []

    def __del__(self):
        SHELL.stop_listen(self.event)

    def register_window(self, window):
        self.windows.append(window)

    def unregister_window(self, window):
        if window in self.windows:
            self.windows.remove(window)
        else:
            raise TclError(6)

    def focus(self, window):
        if window in self.windows:
            self.windows.sort(key=window.__eq__)
        else:
            raise TclError(0, window)

    def event(self, event):
        if event == "ctrl+up":
            CURSOR.move_by(0, -1)
            event = "move_mouse_up"
        elif event == "ctrl+down":
            event = "move_mouse_down"
            CURSOR.move_by(0, 1)
        elif event == "ctrl+left":
            event = "move_mouse_left"
            CURSOR.move_by(-1, 0)
        elif event == "ctrl+right":
            CURSOR.move_by(1, 0)
            event = "move_mouse_right"
        if event == "unknown":
            raise
        for window in self.windows:
            window.event(event)
        DEFAULT_SCREEN.update()

    def update(self):
        self.write()

    def write(self):
        WRITING_CURSOR.clear()
        for window in self.windows:
            window.write()
        CURSOR.show()
        STDOUT.flush()


DEFAULT_SCREEN = Screen()


class Event:
    def __init__(self, event, master):
        self.event = event
        self.master = master
        self.names, self.key = self.sanitise_event(event)
        self.keysym = self.char = self.key

    def sanitise_event(self, event):
        if event == "ctrl+g":
            return ("<Button-1>", ), "??"
        if event in str(string.ascii_lowercase):
            return ("<Key>", event), event
        if "mouse" in event:
            return ("<Motion>", ), "??"
        if event in ("up", "down", "left", "right"):
            return ("<Key>", ), event
        else:
            return event, "??"


class GridManager:
    def __init__(self):
        self.min = (0, 0)
        self.max = (0, 0)
        self.size = (20, 10)
        self.matrix = [[None for i in range(20)] for i in range(20)]
        self.sizes_matrix = [[0 for i in range(20)], [0 for i in range(20)]]

    def add_widget(self, widget):
        if self.destroyed:
            raise TclError(5)
        self.widgets.append(widget)

    def grid(self, widget, row, column):
        if self.destroyed:
            raise TclError(5)
        if widget not in self.widgets:
            raise TclError(4)
        else:
            self.matrix[row][column] = widget
        self.update_sizes_matrix()

    def update_sizes_matrix(self):
        if self.destroyed:
            raise TclError(5)

        for i, widget_list in enumerate(self.matrix):
            for widget in widget_list:
                if widget is not None:
                    new_x = widget.space_needed[0]
                    self.sizes_matrix[0][i] = max(new_x,self.sizes_matrix[0][i])
        for i, widget_list in enumerate(zip(*self.matrix)):
            for widget in widget_list:
                if widget is not None:
                    new_y = widget.space_needed[1]
                    self.sizes_matrix[1][i] = max(new_y, self.sizes_matrix[1][i])

        self.size = (sum(self.sizes_matrix[0]), sum(self.sizes_matrix[1]))
        self.min = (self.position[0]+1, self.position[1]+3)
        self.max = (self.min[0]+self.size[0]-1, self.min[1]+self.size[1]-1)

    def write(self):
        for i, widget_list in enumerate(self.matrix):
            for j, widget in enumerate(widget_list):
                if widget is not None:
                    x = sum(self.sizes_matrix[0][:i])
                    y = sum(self.sizes_matrix[1][:j])
                    widget.position = (x, y)
                    widget.write(self.min, self.max)


class Tk(GridManager):
    def __init__(self):
        super().__init__()
        self.binds = []
        self._title = "Not tk"
        self.widgets = []
        DEFAULT_SCREEN.register_window(self)
        self.position = (0, 1)
        self.hidden = False
        self.destroyed = False

    def destroy(self):
        if self.destroyed:
            raise TclError(5)
        self.destroyed = True
        for widget in self.widgets:
            widget.destroy()
        DEFAULT_SCREEN.unregister_window(self)

    def bind(self, sequence, function):
        self.binds.append((sequence, function))

    def protocol(self, protocol, function):
        if protocol == "WM_DELETE_WINDOW":
            self.bind("<Destroy>", function)

    def event(self, event):
        sanitised_event = Event(event, self)
        for seq, func in self.binds:
            if seq in sanitised_event.names:
                func(sanitised_event)

        if event == "ctrl+g":
            x, y = self.position
            if tuple(CURSOR.position) == (x+self.size[0], y+1):
                self.event("destroy")
                self.destroy()

        for widget in self.widgets:
            widget.event(event)

    def title(self, string):
        self._title = string

    def geometry(self, string):
        if self.destroyed:
            raise TclError(5)
        if string.count("+") not in (0, 2):
            raise TclError(2)
        if string.count("x") not in (0, 1):
            raise TclError(2)
        if string.count("+") == 2:
            part1, pos_x, pos_y = string.split("+")
            self.position = (int(pos_x), int(pos_y))
            string = part1
        if string.count("x") == 1:
            size_x, size_y = string.split("x")
            self.size = (int(size_x), int(size_y))

    def hide(self):
        if self.destroyed:
            raise TclError(5)
        self.hidden = True

    def resizable(self, x=None, y=None):
        pass

    def update(self):
        if self.destroyed:
            raise TclError(5)
        DEFAULT_SCREEN.update()

    def mainloop(self):
        if self.destroyed:
            raise TclError(5)
        while not self.destroyed:
            self.update()

    def write(self):
        screen = WRITING_CURSOR
        if self.destroyed:
            raise TclError(5)
        """
        A -------- B
        | Tk      X|
        C -------- D
        |          |
        |          |
        |          |
        E -------- F
        """
        if self.hidden:
            return None
        size_x, size_y = self.size

        x, y = self.position
        A = (x, y)
        D = (x+size_x+2, y+3)
        F = (x+size_x+2, y+size_y+4)

        screen.draw_rectangle(A, D, charh="═", charv="║", corners="╔╗╚╝")
        screen.draw_rectangle(A, F, charh="═", charv="║", corners="╔╗╚╝")

        if F[0] > DEFAULT_SIZE[0]:
            self.size = (self.size[0]-(F[0]-DEFAULT_SIZE[0]), self.size[1])
            size_x, size_y = self.size
            F = (x+size_x+2, y+size_y+4)
        if F[1] > DEFAULT_SIZE[1]:
            self.size = (self.size[0], self.size[1]-(F[1]-DEFAULT_SIZE[1]))
            size_x, size_y = self.size
            F = (x+size_x+2, y+size_y+4)

        screen[x, y+2] = "╠"
        screen[x+size_x+1, y+2] = "╣"
        screen[x+size_x, y+1] = "X"

        screen[x+2, y+1] = self._title[:self.size[0]-2]
        super().write()


class Widget:
    def __init__(self, master):
        self.binds = []
        self.master = master
        master.add_widget(self)
        self.space_needed = (0, 0)
        self.destroyed = False

    def grid(self, row, column):
        if self.destroyed:
            raise TclError(3)
        self.master.grid(self, row, column)

    def bind(self, sequence, function):
        self.binds.append((sequence, function))

    def event(self, event):
        event = Event(event, self)
        for seq, func in self.binds:
            if seq in event.names:
                func(event)

    def destroy(self):
        self.destroyed = True
        self.space_needed = (0, 0)


class Label(Widget):
    def __init__(self, master, text="", bg=None, fg=None,
                 modifiers=None):
        super().__init__(master)
        self.bg = ""
        self.fg = ""
        self.config(text=text, bg=bg, fg=fg)
        self.space_needed = (len(self.text), 1)

    def config(self, text=None, bg=None, fg=None, modifiers=None):
        if bg is not None:
            self.bg, _ = shell.colour_to_code(bg, fg=False)
        if fg is not None:
            self.fg, _ = shell.colour_to_code(fg, fg=True)
        if text is not None:
            self.text = text
        self.space_needed = (len(self.text), 1)

    def write(self, min, max):
        start_x = self.position[0]+self.master.position[0]+1
        start_y = self.position[1]+self.master.position[1]+3
        coords = (start_x, start_y)
        WRITING_CURSOR.set(*coords, self.text, min, max, self.fg+self.bg)


class Button(Widget):
    def __init__(self, master, text="", command=None,
                 bg=None, fg="blue", modifiers=None):
        super().__init__(master)
        self.mods = shell.UNDERLINED
        self.bg = ""
        self.fg = ""
        self.command = None
        self.config(text=text, command=command, bg=bg, fg=fg,
                    modifiers=modifiers)

    def config(self, text=None, command=None, bg=None, fg=None, modifiers=None):
        if text is not None:
            self.text = text
            self.space_needed = (len(self.text), 1)
        if command is not None:
            self.command = command
        if bg is not None:
            self.bg, _ = shell.colour_to_code(bg, fg=False)
        if fg is not None:
            self.fg, _ = shell.colour_to_code(fg, fg=True)

    def write(self, min, max):
        start_x = self.position[0]+self.master.position[0]+1
        start_y = self.position[1]+self.master.position[1]+3
        coords = (start_x, start_y)
        mods = self.mods+self.bg+self.fg
        WRITING_CURSOR.set(*coords, self.text, min, max, mods)

    def event(self, event):
        if event == "ctrl+g":
            start_x = self.position[0]+self.master.position[0]+1
            y = self.position[1]+self.master.position[1]+3
            end_x = start_x + len(self.text)
            pos = CURSOR.position
            if (start_x <= pos[0] < end_x) and (pos[1] == y):
                if self.command is not None:
                    self.command(event)
        super().event(event)


class Canvas(Widget):
    def __init__(self, master, height, width, bg=None, PIXELS_PER_CHAR=None):
        if PIXELS_PER_CHAR is None:
            self.PIXELS_PER_CHAR_X = 10
            self.PIXELS_PER_CHAR_Y = 20 # to make it into squares
        elif isinstance(PIXELS_PER_CHAR, int):
            self.PIXELS_PER_CHAR_X = PIXELS_PER_CHAR
            self.PIXELS_PER_CHAR_Y = PIXELS_PER_CHAR
        else:
            self.PIXELS_PER_CHAR_X = PIXELS_PER_CHAR[0]
            self.PIXELS_PER_CHAR_Y = PIXELS_PER_CHAR[1]

        super().__init__(master)
        self.bg = bg or "white"
        self.sprite_number = 0
        self.sprites = []
        self.sprites_args = {}
        self.CHAR_HEIGHT = height//self.PIXELS_PER_CHAR_Y
        self.CHAR_WIDTH = width//self.PIXELS_PER_CHAR_X
        self.space_needed = (self.CHAR_WIDTH, self.CHAR_HEIGHT)

    def write(self, min, max):
        start_x = self.position[0]+self.master.position[0]+1
        start_y = self.position[1]+self.master.position[1]+3
        if self.bg != "black":
            bg = shell.colours_only(shell.colour_to_code(self.bg, fg=None))
            for i in range(min[0], max[0]+1):
                for j in range(min[1], max[1]+1):
                    WRITING_CURSOR.set(i, j, "█", min, max, bg)
        for sprite in self.sprites[::-1]:
            args = self.sprites_args[sprite]
            fill = args["colour"]
            char = args["char"]
            for x, y in args["positions"]:
                WRITING_CURSOR.set(start_x+x, start_y+y, char, min, max, fill)

    def create_rectangle(self, x1, y1, x2, y2, fill, **kwargs):
        x1 = x1//self.PIXELS_PER_CHAR_X
        x2 = (x2+1)//self.PIXELS_PER_CHAR_X
        y1 = y1//self.PIXELS_PER_CHAR_Y
        y2 = (y2+1)//self.PIXELS_PER_CHAR_Y
        if (x1 == x2) or (y1 == y2):
            return None
        _sprite = self.sprite_number
        self.sprites.append(_sprite)
        positions = []
        for x in range(x1, x2):
            for y in range(y1, y2):
                positions.append((x, y))

        colour = shell.colours_only(shell.colour_to_code(fill, fg=None))
        args = {"positions": tuple(positions),
                "colour": colour,
                "char": "█"}
        self.sprites_args.update({_sprite: args})
        self.sprite_number += 1
        return _sprite

    def delete(self, what):
        if what == "all":
            self.sprites.clear()
            self.sprites_args = {}
        else:
            if what in self.sprites:
                self.sprites.remove(what)
                self.sprites_args.pop(what)
            else:
                raise TclError(7)


if __name__ == "__main__":
    root = Tk()
    root.title("Not tk")
    l = Label(root, text="Hello")
    l.grid(row=0, column=0)
    l = Label(root, text="world")
    l.grid(row=1, column=1)
    root.mainloop()
