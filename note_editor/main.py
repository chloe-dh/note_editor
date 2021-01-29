import configparser
import os
import tkinter as tk
from tkinter import filedialog

from note_editor.notes_class import NoteManager, SelectNote, NoteWindow
from note_editor.pdf_maker import make_pdf


class MainWindow:
    def __init__(self):
        # load config for save path
        self.config = configparser.ConfigParser()
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        self.config.read(self.config_path)
        # main window
        self.root = tk.Tk()
        self.root.title('note on stuff')
        self.root.resizable(True, True)
        self.root.bind('<Escape>', func=self.exit_gui)
        self.root.bind('<Return>', func=self.on_return)
        # saves pdf upon manually closing
        self.root.protocol("WM_DELETE_WINDOW", self.exit_gui)
        # instantiate attributes
        self.select_window = None
        self.opened_note_window = 0
        # create buttons:
        self.bd = 10
        self.width = 15
        self.new_note_btn = tk.Button(self.root,
                                      text="New note",
                                      command=self.new_note,
                                      bd=self.bd,
                                      width=self.width,
                                      highlightthickness=2
                                      )
        self.edit_btn = tk.Button(self.root,
                                  text="Edit / Delete",
                                  command=self.select_note,
                                  bd=self.bd,
                                  width=self.width,
                                  highlightthickness=2
                                  )
        self.save_as_btn = tk.Button(self.root,
                                     text="Set pdf pathname",
                                     command=self.save_as,
                                     bd=self.bd,
                                     width=self.width,
                                     highlightthickness=2
                                     )
        # a label to show where the pdf is being saved
        self.save_label = tk.Label(self.root)

        # pack all widgets:
        self.new_note_btn.pack()
        self.edit_btn.pack()
        self.save_as_btn.pack()
        self.save_label.pack()
        # load values
        self.note_manager = NoteManager()
        self.write_label()

    def new_note(self):
        # close selection window
        if self.select_window:
            self.select_window.exit_window()
        # limit max number of opened windows
        if self.opened_note_window < 4:
            NoteWindow(self)
            self.opened_note_window += 1

    def select_note(self):
        # closes previous and open new one
        if self.select_window:
            self.select_window.exit_window()
        self.select_window = SelectNote(self)

    def save_as(self):
        head = self.config['save_path']['head']
        tail = self.config['save_path']['tail']
        file = filedialog.asksaveasfilename(initialdir=head, initialfile=tail, defaultextension='.pdf')
        # update config if filedialog exits with a value
        if file:
            head, tail = os.path.split(file)
            self.config['save_path']['head'] = head
            self.config['save_path']['tail'] = tail
            with open(self.config_path, 'w') as f:
                self.config.write(f)
        # update label
        self.write_label()

    def write_label(self):
        head = self.config['save_path']['head']
        tail = self.config['save_path']['tail']
        self.save_label['text'] = str(os.path.join(head, tail))

    def on_return(self, event):
        # implement return behavior, unless no focus is set
        widget = self.root.focus_get()
        try:
            widget.invoke()
        except AttributeError:
            pass

    def exit_gui(self, *args):
        path = os.path.join(self.config['save_path']['head'], self.config['save_path']['tail'])
        # try:
        make_pdf(path, self.note_manager)

        self.root.destroy()


def run():
    gui = MainWindow()
    gui.root.mainloop()


if __name__ == '__main__':
    run()
