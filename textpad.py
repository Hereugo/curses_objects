# Very similiar to textpad example given in curses module


import curses
from curses import window, ascii
from utils import rectangle, iscyrillic


class Textpad:

    def _update_max_yx(self):
        maxy, maxx = self.win.getmaxyx()
        self.maxy = maxy - 1
        self.maxx = maxx - 1

    def __init__(self, stdscr: window, label: str):
        stdscr.clear()
        curses.curs_set(True)

        height, width = stdscr.getmaxyx()
        ncols, nlines = width // 2, 1

        uly, ulx = height // 2 - nlines // 2, width // 2 - ncols // 2

        # TODO: Print instructions in top-left corner.
        ...

        stdscr.addstr(uly - 2, ulx - 1, label)
        rectangle(stdscr, uly - 1, ulx - 1, uly + nlines, ulx + ncols)

        stdscr.refresh()
        self.win = curses.newwin(nlines, ncols, uly, ulx)
        self.input_text = ""
        self.offset_by = 0

        self.win.keypad(True)
        self.win.nodelay(True)

    # TODO:
    # Doesn't respond to cyrcilicc characters
    def do_command(self, ch: int) -> bool:
        """
        Several Cases:
        1. user inputs a character -> adds to screen
        2. user presses enter -> confirmation of input, exists program
        3. user moves arrow keys left or right -> moves input accordingly
        """
        self._update_max_yx()
        (y, x) = self.win.getyx()
        if ch in (
            curses.KEY_LEFT,
            ascii.STX,
            ascii.BS,
            curses.KEY_BACKSPACE,
            ascii.DEL,
        ):
            if x == 1:
                if self.offset_by > 0:
                    self.offset_by -= 1
            else:
                x -= 1
            self.win.move(y, x)
            # Delete characters
            if ch in (ascii.BS, curses.KEY_BACKSPACE, ascii.DEL):
                index = self.offset_by + x
                self.input_text = self.input_text[: index - 1] + self.input_text[index:]

                self.win.delch()
        elif ch in (curses.KEY_RIGHT,) or ascii.isprint(ch):
            # Add characters
            if ascii.isprint(ch) or iscyrillic(ch):
                index = self.offset_by + x - 1
                self.input_text = (
                    self.input_text[:index] + chr(ch) + self.input_text[index:]
                )

            if x == self.maxx:
                self.offset_by += 1
            elif self.offset_by + x <= len(self.input_text):
                x += 1
            self.win.move(y, x)
        elif ch in (curses.KEY_ENTER, 10):
            return False
        elif ch in (ascii.ESC,):  # Terminate program with exit code 1
            exit(1)
        else:  # Do nothing, if an invalid character was given
            pass

        return True

    def display(self):
        self._update_max_yx()
        (y, x) = self.win.getyx()
        visible_text = self.input_text[self.offset_by : self.offset_by + self.maxx - 1]
        self.win.addstr(0, 1, visible_text)
        self.win.move(y, x)

    def edit(self):
        """Edit textpad"""
        self.win.move(0, 1)
        while True:
            self.win.refresh()
            self.display()
            ch = self.win.getch()
            if not self.do_command(ch):
                break
        return self.input_text


if __name__ == "__main__":
    label: str = "This is a label"

    def display_textpad(stdscr: window):
        return Textpad(stdscr, label).edit()

    input_data: str = curses.wrapper(display_textpad)

    print("Inputted:", input_data)
