from mytkinter import Tk, Canvas

import time
from random import randint

class App:
    def __init__(self, height=300, width=300, pixel_size=20):
        self.width = width
        self.height = height
        self.game_over = False
        self.momentum = (1, 0)
        self.pix_size = pixel_size
        self.snake = [(0, 0), (0, 1), (0, 2)]
        self.last_moved_snake_time = time.time()
        self.pix_numb_x = self.width//self.pix_size
        self.pix_numb_y = self.height//self.pix_size
        self.new_goal()

        self.root = Tk()
        self.master = Canvas(self.root, height=height, width=width, bg="black")
        self.master.grid(row=0, column=0)
        self.root.bind("<Key>", self.key_pressed)
        self.display()

    def __del__(self, *args, **kwargs):
        self.root.destroy()

    def new_goal(self):
        self.goal_position = self.snake[0] # Force the loop
        while self.goal_position in self.snake:
            x = randint(0, self.pix_numb_x-1)
            y = randint(0, self.pix_numb_y-1)
            self.goal_position = (x, y)

    def key_pressed(self, event):
        key = event.char.lower()
        keysum = event.keysym.lower()
        if key == "w" or keysum == "up":
            if self.momentum == (0, 1):
                self.game_over = True
            self.momentum = (0, -1)
        elif key == "s" or keysum == "down":
            if self.momentum == (0, -1):
                self.game_over = True
            self.momentum = (0, 1)
        elif key == "a" or keysum == "left":
            if self.momentum == (1, 0):
                self.game_over = True
            self.momentum = (-1, 0)
        elif key == "d" or keysum == "right":
            if self.momentum == (-1, 0):
                self.game_over = True
            self.momentum = (1, 0)
        if self.game_over:
            self.display()

    def display(self):
        self.master.delete("all")
        self.display_snake()
        self.display_goal()

    def display_pixel(self, x, y, colour="white"):
        x *= self.pix_size
        y *= self.pix_size
        x2 = x+self.pix_size-1
        y2 = y+self.pix_size-1
        self.master.create_rectangle(x, y, x2, y2, fill=colour, outline=colour)

    def display_snake(self):
        for part_of_snake in self.snake[:-1]:
            if self.game_over:
                self.display_pixel(*part_of_snake, colour="red")
            else:
                self.display_pixel(*part_of_snake)

        head = self.snake[-1]

        self.display_pixel(*head, colour="yellow")

    def display_goal(self):
        self.display_pixel(*self.goal_position, colour="light blue")

    def move_snake(self):
        new_head_position = (self.snake[-1][0]+self.momentum[0],
                             self.snake[-1][1]+self.momentum[1])
        if self.check_dead(*new_head_position):
            self.game_over = True
        else:
            self.snake += [new_head_position]
            if new_head_position == self.goal_position:
                self.new_goal()
            else:
                del self.snake[0]

    def check_dead(self, new_head_x, new_head_y):
        if self.pix_numb_x > new_head_x >= 0:
            if self.pix_numb_y > new_head_y >= 0:
                return (new_head_x, new_head_y) in self.snake
        return True

    def update(self):
        if time.time()-self.last_moved_snake_time >= 0.15:
            self.move_snake()
            self.last_moved_snake_time = time.time()
        self.display()
        self.root.update()

game = App()
while not game.game_over:
    game.update()

# https://www.nutc.site/
