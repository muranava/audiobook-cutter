#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

import pyglet
import codecs

JOINED_PARAGRAPH_MAX_SIZE = 350
SPLIT_AFTER_LENGTH = 400
FONT_NAME="WenQuanYi Micro Hei Mono"

window = pyglet.window.Window()
label = pyglet.text.Label("", font_name=FONT_NAME, anchor_y='bottom', width=window.width, multiline=True)
audio = pyglet.resource.media('input.mp3')
player = pyglet.media.Player()
player.queue(audio)


def split_paragraph(paragraph):
    splits = []

    paragraph_so_far = ""
    split_after_length = SPLIT_AFTER_LENGTH
    
    sentence_enders = [u"。", u"！", u"？"]
    
    for char in paragraph:
        if char in sentence_enders and len(paragraph_so_far) > split_after_length:        
            splits.append(paragraph_so_far + char)
            paragraph_so_far = ""
        else:
            paragraph_so_far = paragraph_so_far + char

    if len(paragraph_so_far) > 0:
        splits.append(paragraph_so_far)
            
    return splits

def pack_paragraphs(paragraphs):
    joined_paragraph_max_size = JOINED_PARAGRAPH_MAX_SIZE

    new_paragraph_list = []
    current_paragraph = ""

    for paragraph in paragraphs:
        if current_paragraph == "":
            current_paragraph = paragraph
        elif len(current_paragraph) + len(paragraph) < joined_paragraph_max_size:
            current_paragraph = current_paragraph + "\\n" + paragraph
        else:
            new_paragraph_list.append(current_paragraph)
            current_paragraph = paragraph
    
    if current_paragraph != "":
        new_paragraph_list.append(current_paragraph)

    return new_paragraph_list


 
class Main:
    def main(self):
        self.completed_lines = []
        self.input_text = codecs.open('input.txt', 'r', 'utf-8')
        self.input_lines = self.input_text.readlines()

        self.paused = False

        non_empty_lines = []
        for line in self.input_lines:
            choped_line = line.replace("\n", "")
            split_lines = split_paragraph(choped_line)
            for split_line in split_lines:
                if len(split_line) > 0:
                    non_empty_lines.append(split_line)
        
        
        self.input_lines = pack_paragraphs(non_empty_lines)

        self.curr_line = "" 
        self.curr_timestamp = 0

        self.read_rate_chars_per_sec = 4.5
        
        player.play()
        self.first_line()
        pyglet.app.run()

    def get_completed_lines(self):
        return self.completed_lines

    def first_line(self):
        self.curr_line = self.input_lines.pop(0)
        self.display_text(self.curr_line)

        

    def next_line(self):
	next_timestamp = self.get_next_timestamp()
        piece_length = next_timestamp - self.curr_timestamp
        self.completed_lines.append((self.curr_timestamp, piece_length, self.curr_line))

        if len(self.input_lines) == 0:
            return
        else:
            self.curr_timestamp = next_timestamp
            self.curr_line = self.input_lines.pop(0)
            self.display_text(self.curr_line)

    def skip_line(self):
        self.curr_line = self.input_lines.pop(0)
        self.display_text(self.curr_line)

    def update_timestamp(self):
        if len(self.input_lines) > 0:
            self.curr_timestamp = self.get_next_timestamp()

    
    def get_next_timestamp(self):
        if player.playing:
            timestamp = player.time
        else:
            timestamp = player.source.duration
        return timestamp
    

    def fast_forward_to_line_end(self):
        
        advance_seconds = len(self.curr_line) / self.read_rate_chars_per_sec
        seek_to = self.curr_timestamp + advance_seconds
        print "fast_forward_to_line_end", seek_to, " - " , advance_seconds,  len(self.curr_line), "/" , self.read_rate_chars_per_sec
        player.seek(seek_to)
        player.play()


    def back_nsec(self, n):
        seek_to = int(player.time - n)
        if seek_to < 0:
            seek_to = 0
        print seek_to
        player.seek(seek_to)
        player.play()

    def forward_nsec(self, n):
        seek_to = int(player.time + n)
        print seek_to
        player.seek(seek_to)
        player.play()
        

    def on_draw(self):
        window.clear()
        label.draw()

    @window.event
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            if self.paused:
                player.play()
                self.paused = False
            else:
                player.pause()                
                self.paused = True
        if symbol == pyglet.window.key.ENTER:
            print "enter"            
            self.next_line()
        if symbol == pyglet.window.key.N:
            print "N"
            self.skip_line()
        if symbol == pyglet.window.key.T:
            print "T"
            self.update_timestamp()
        if symbol == pyglet.window.key.P:
            self.read_rate_chars_per_sec = self.read_rate_chars_per_sec + 0.1
            print "read_rate_chars_per_sec", self.read_rate_chars_per_sec
        if symbol == pyglet.window.key.O:
            self.read_rate_chars_per_sec = self.read_rate_chars_per_sec - 0.1
            print "read_rate_chars_per_sec", self.read_rate_chars_per_sec
        if symbol == pyglet.window.key.LEFT:
            print "LEFT"
            self.back_nsec(5)
        if symbol == pyglet.window.key.RIGHT:
            print "RIGHT"
            self.forward_nsec(5)
        if symbol == pyglet.window.key.PAGEUP:
            print "LEFT"
            self.back_nsec(60)
        if symbol == pyglet.window.key.PAGEDOWN:
            print "RIGHT"
            self.forward_nsec(60)
        if symbol == pyglet.window.key.F:
            print "FAST FORWARD"
            self.fast_forward_to_line_end()




    def display_text(self, thetext):
        thetext =  thetext.replace("\\n", "\n")
        display_text= u''
        charCounter=0
        for char in thetext:
            if char == "\n":
                charCounter = 0
            display_text = display_text + char
            charCounter = charCounter + 1
            if charCounter % 39 == 0:
                display_text = display_text + "\n"

        label.text = display_text

m = Main()

@window.event
def on_draw():
    m.on_draw()

@window.event
def on_key_press(symbol, modifiers):
    m.on_key_press(symbol, modifiers)


m.main()

print "ending"

output = codecs.open('output.txt', 'w', 'utf-8')
line_counter = 1
for timestamp, length, line in m.get_completed_lines():
    output.write(str(line_counter))
    output.write("=")
    output.write(str(timestamp))
    output.write("=")
    output.write(str(length))
    output.write("=")
    output.write(line)
    output.write("\n")
    line_counter = line_counter + 1



