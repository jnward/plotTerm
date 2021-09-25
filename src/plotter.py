import serial
import time
import numpy as np
import json

from font import primitives

CHAR_WIDTH = 7/2
CHAR_HEIGHT = 9/2

EM_WIDTH = 7/2
EM_HEIGHT = 10/2

Y_HEIGHT = 235

def map_points(points):
    return np.array(points).reshape(-1, 2) / [7, 9] * [CHAR_WIDTH, CHAR_HEIGHT]


class Plotter:
    def __init__(self, x_off, y_off, debug=False):
        self.ser = serial.Serial('/dev/ttyUSB0', 115200)
        self.x_off = x_off
        self.y_off = y_off
        self.char_idx = 0
        self.num_cols = ((Y_HEIGHT-x_off) // EM_WIDTH) - 1
        self.debug = debug
        self.show_offset = 40
        self.y_max = Y_HEIGHT-y_off-self.show_offset
        self.reset()
        
    @property
    def _next_char_col(self):
        return self.char_idx % self.num_cols
    
    @property
    def _next_char_row(self):
        return self.char_idx // self.num_cols
        
    def send(self, instruction):
        time.sleep(0.1)
        if self.debug: print(instruction)
        self.ser.write(instruction.encode('ascii'))
        
        while True:
            line = self.ser.readline()
            if self.debug: print(line)
            if line == b'ok\n':
                break
        
    def reset(self):
        self.send('G28\n')
        self.home()
        
    def home(self):
        self._up()
        self.send(f'G0 X0 Y{self.y_max} Z2 F2000\n')
        self._down()

    def show(self):
        y = self.y_max - (self.y_off + EM_HEIGHT * self._next_char_row) + self.show_offset
        self._up()
        self.send(f'G0 Y{y} F5000\n')
        
    def _up(self):
        self.send('G1 Z2 F1000\n')
        
    def _down(self):
        self.send('G1 Z1 F1000\n')
        
    def move(self, x, y):
        self._up()
        cmd = f'G0 X{x} Y{y} Z2 F5000\n'
        self.send(cmd)
        
    def draw(self, x, y):
        cmd = f'G1 X{x} Y{y} Z1 F1000\n'
        self.send(cmd)
        
    def point(self, x, y):
        self.move(x-0.5, y-0.5)
        self._down()
        self.draw(x+0.5, y+0.5)
        self._up()
        
    def print_char(self, char):
        if char == '\n':
            self.char_idx += self.num_cols - self.char_idx % self.num_cols
        else:
            self.char_primitive(char)
            self.char_idx += 1
        
    def char_part(self, points):
        x = self.x_off + EM_WIDTH * self._next_char_col
        y = self.y_max - (self.y_off + EM_HEIGHT * self._next_char_row)
        points = map_points(points) + [x, y]
        self.move(*points[0])
        self._down()
        self.draw(*points[0])
        for i in range(len(points) - 1):
            p = points[i+1]
            self.draw(*p)
        self._up()
        
    def char_primitive(self, char):
        paths = primitives.get(char, primitives['.'])
        for path in paths:
            self.char_part(path)
            
    def print_string(self, string):
        for c in string:
            self.print_char(c)

if __name__=='__main__':
    plot = Plotter(60, 20, debug=True)
    plot.print_string('test')
    plot.home()
