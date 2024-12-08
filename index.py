import curses
from textpad import Textpad
from select import Select

if __name__ == "__main__":

    def display_select(stdsrc: curses.window):
        return Select(
            stdsrc, "select title", ["this is one", "this is two", "this is three"]
        ).select()

    def display_textpad(stdsrc: curses.window):
        return Textpad(stdsrc, "Input data: ").edit()

    select_data = curses.wrapper(display_select)
    textpad_data = curses.wrapper(display_textpad)

    print(select_data)
    print(textpad_data)
