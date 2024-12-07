import curses
from curses import window, ascii
from typing import Generic, TypeVar

T = TypeVar("T")


def rectangle(win, uly, ulx, lry, lrx):
    """Draw a rectangle with corners at the provided upper-left
    and lower-right coordinates.
    """
    win.vline(uly + 1, ulx, curses.ACS_VLINE, lry - uly - 1)
    win.hline(uly, ulx + 1, curses.ACS_HLINE, lrx - ulx - 1)
    win.hline(lry, ulx + 1, curses.ACS_HLINE, lrx - ulx - 1)
    win.vline(uly + 1, lrx, curses.ACS_VLINE, lry - uly - 1)
    win.addch(uly, ulx, curses.ACS_ULCORNER)
    win.addch(uly, lrx, curses.ACS_URCORNER)
    win.addch(lry, lrx, curses.ACS_LRCORNER)
    win.addch(lry, ulx, curses.ACS_LLCORNER)


# TODO: Handle dynamic resizing
class Form(Generic[T]):
    """Widget using a window object."""

    def _update_max_yx(self):
        maxy, maxx = self.win.getmaxyx()
        self.maxy = maxy - 1
        self.maxx = maxx - 1

    def __init__(self, stdscr: window, form_title: str, options: list[T]):
        height, width = stdscr.getmaxyx()
        ncols, nlines = width // 2, height // 2

        nlines = min(nlines, len(options))

        uly, ulx = height // 2 - nlines // 2 + 1, width // 2 - ncols // 2 - 1
        stdscr.addstr(
            1,
            1,
            "1. Use arrow keys to move, supports vim motions\n"
            + " 2. press space to select. press space again to confirm. \n"
            + " 3. press ESC to terminate program.",
        )

        rectangle(stdscr, uly - 3, ulx - 1, uly + 3, ulx + ncols)
        rectangle(stdscr, uly - 1, ulx - 1, uly + nlines, ulx + ncols)
        stdscr.addch(uly - 1, ulx - 1, "├")
        stdscr.addch(uly - 1, ulx + ncols, "┤")
        stdscr.addch(uly - 1, ulx + 5, "┬")
        stdscr.addch(uly + nlines, ulx + 5, "┴")

        stdscr.addch(uly - 3, ulx + ncols - 8, "┬")
        stdscr.addch(uly - 1, ulx + ncols - 8, "┴")

        stdscr.refresh()

        self.form_title = form_title
        self.title_win = curses.newwin(1, ncols, uly - 2, ulx)
        self.win = curses.newwin(nlines, ncols, uly, ulx)
        self.options = options
        self.selected_id = None
        self.offset_by = 0
        self._update_max_yx()
        self.win.keypad(True)
        self.win.nodelay(True)
        curses.curs_set(0)

    def do_command(self, ch: int) -> bool:
        """
        Several cases:
        1. ch is an up arrow key -> move selection up
        2. ch is a down arrow key -> move selection down
        3. ch is an enter ->
            3.1 enter pressed once, selects an option.
            3.2 enter pressed twice, confirms selection (ends form).
        4. otherwise, do nothing.
        """
        self._update_max_yx()
        (y, x) = self.win.getyx()
        if ch in (curses.KEY_UP, ord("k")):  # Arrow key UP
            if y == 0:
                if self.offset_by > 0:
                    self.offset_by -= 1
                else:
                    y = self.maxy
                    self.offset_by = len(self.options) - self.maxy - 1
            else:
                y -= 1
            self.win.move(y, x)
        elif ch in (curses.KEY_DOWN, ord("j")):  # Arrow key DOWN
            if y == self.maxy:
                if self.offset_by + self.maxy + 1 < len(self.options):
                    self.offset_by += 1
                else:
                    y = 0
                    self.offset_by = 0
            else:
                y += 1
            self.win.move(y, x)
        elif ch in (ascii.SP,):  # Space
            if (
                self.selected_id != None and self.selected_id == self.offset_by + y
            ):  # CONFIRM
                return False
            else:  # SELECT ENTER
                self.selected_id = self.offset_by + y
            self.win.move(y, x)
        elif ch in (ascii.ESC,):  # Terminate program with exit code 1
            exit(1)
        else:  # Do nothing, if an invalid character was given
            pass
        return True

    def display(self):
        """Display all options."""
        self._update_max_yx()
        (y, x) = self.win.getyx()
        self.win.move(y, x)

        # Update progress bar in title
        self.title_win.addstr(0, 0, " " * (self.maxx - 1))
        percent = int((self.offset_by + y + 1) / len(self.options) * 100)
        progress_text = f"│  {str(percent).rjust(2, "0")}%"
        progress_size = 7

        if self.offset_by + y == 0:
            progress_text = "│  TOP"
        elif self.offset_by + y == len(self.options) - 1:
            progress_text = "│  BOT"

        self.title_win.addstr(0, 1, self.form_title[: self.maxx - progress_size])
        self.title_win.addstr(0, self.maxx - len(progress_text) - 1, progress_text)

        # Clear screen
        for i in range(self.maxy + 1):
            text = f"    │".ljust(self.maxx - 1, " ")
            self.win.addstr(i, 1, text)
        self.win.move(y, x)

        # Display selection content
        visible_options = self.options[self.offset_by : self.offset_by + self.maxy + 1]
        for i, option in enumerate(visible_options, 1):
            str_option = str(option)
            is_selected = self.selected_id == self.offset_by + i - 1

            selected = "(x)" if is_selected else "( )"

            text = f"{selected} │ {str_option}".ljust(self.maxx - 1, " ")

            # TODO: Truncate with ... at the end
            text = text[: self.maxx]

            if is_selected:
                self.win.addstr(i - 1, 1, text, curses.A_STANDOUT)
            elif y == i - 1:
                self.win.addstr(i - 1, 1, text, curses.A_UNDERLINE)
            else:
                self.win.addstr(i - 1, 1, text)

        self.win.move(y, x)

    def select(self) -> T:
        """
        selection options in the widget window, and return the selected option.
        """
        # Move to beginning of selection options
        self.win.move(1, 2)
        while True:
            self.win.refresh()
            self.title_win.refresh()
            self.display()
            ch = self.win.getch()
            if not self.do_command(ch):
                break

        assert (
            self.selected_id != None
        ), "selected id must have a value upon end, but None was given."

        return self.options[self.selected_id]


if __name__ == "__main__":
    form_title: str = (
        "Client Form this is a super long text that should be truncated apple apple apple"
    )
    options = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
    ]

    def display_form(stdscr: window):
        return Form(stdscr, form_title, options).select()

    form_data = curses.wrapper(display_form)
    print("Form data:", form_data)
