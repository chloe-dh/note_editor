import csv
import os
import tkinter as tk
from collections import namedtuple
from functools import partial
from tkinter import ttk

list_media = ['book', 'movie', 'comic-book', 'short movie', 'podcast', 'drawing', 'leaflet', '']
Category = namedtuple('Category', ['name', 'cat_type', 'values'])
# order matters
categories = (
            Category('title', 'entry', None),       # needs to be 1st
            Category('author', 'entry', None),
            Category('year', 'entry', None),
            Category('subtitle', 'entry', None),
            Category('media_type', 'combo', list_media),
            Category('episode', 'entry', None),
            Category('link', 'entry', None),
            Category('one_liner', 'entry', None),   # better if this stays one to last
            Category('notes', 'text', None)         # needs to be last
      )


class NoteManager:
    """list of notes which are dict with category names as keys
    the category attribute is a tuple with info regarding the category """

    def __init__(self):
        self.list = []
        self.categories = categories
        self.select_window_open = False
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notes.csv')
        self.load()

    def load(self):
        """load current version of notes.csv"""
        if os.path.exists(self.path):
            with open(self.path) as p:
                for row in csv.DictReader(p, skipinitialspace=True):
                    self.list.append({k: v for k, v in row.items()})

    def dump(self):
        """write current version of note_manager to file and backup version n-1"""
        """update pdf file"""
        # if current exists, rename to backup
        if os.path.exists(self.path):
            base, ext = os.path.splitext(self.path)
            os.rename(self.path, base + "_backup" + ext)
        # write to file
        keys = [cat.name for cat in self.categories]
        with open(self.path, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.list)

    def add_note(self, note):
        """add note to the note manager class then write to file"""
        self.list.append(note)
        self.dump()

    def remove_note(self, note_number):
        """remove note from note manager class then write to file"""
        self.list.pop(note_number)
        self.dump()

    def update_note(self, note, note_number):
        """update note by removing previous version and adding new one"""
        self.remove_note(note_number)
        self.add_note(note)
        self.dump()

    def new_empty_note(self):
        """generate empty note dictionary"""
        return {category.name: '' for category in self.categories}


def select_all(event, cat_type):
    """function for selecting all text in widget"""
    btn = event.widget
    if cat_type == 'entry':
        btn.select_range(0, 'end')
        btn.icursor('end')
    else:  # cat_type == text
        btn.tag_add(tk.SEL, "1.0", tk.END)
        btn.mark_set(tk.INSERT, "1.0")
        btn.see(tk.INSERT)
        return 'break'


class NoteWindow:
    """Generate a note editor window for writing a new note or editing a previous one"""
    def __init__(self, main, note_number=None):
        # window design
        self.parent = main
        self.root = tk.Toplevel(self.parent.root)
        self.root.title('Note editor')
        self.root.resizable(True, True)
        # close without saving upon hitting escape
        self.root.bind('<Escape>', func=self.exit_window)
        self.root.bind('<Control-Return>', func=self.set_save_focus)
        # make arguments class attribute
        self.categories = self.parent.note_manager.categories
        self.note_manager = self.parent.note_manager
        self.note_number = note_number
        # load existing values or create empty note
        if type(self.note_number) == int:
            self.note = self.note_manager.list[self.note_number]
        else:
            self.note = self.note_manager.new_empty_note()
        self.entry_width = 35

        # one frame per category with one label and one input
        self.cat_frames = {cat.name: None for cat in self.categories}
        self.labels = {cat.name: None for cat in self.categories}
        self.inputs = {cat.name: None for cat in self.categories}

        # populate window
        self.populate()
        # focus on first entry field
        self.inputs[self.categories[0].name].focus()

        # buttons
        self.button_frame = self.cat_frames[self.categories[0].name]
        self.save_button = tk.Button(self.button_frame,
                                     text='Exit and save',
                                     command=self.save_exit,
                                     takefocus=0)
        self.delete_button = tk.Button(self.button_frame,
                                       text='Delete note',
                                       command=self.delete_note,
                                       takefocus=0)
        self.delete_button.pack(side=tk.RIGHT)
        self.save_button.pack(side=tk.RIGHT)

    def populate(self):
        """generate labels and input fields"""
        for name, cat_type, values in self.categories:
            # one frame per category for horizontal packing
            self.cat_frames[name] = tk.Frame(self.root)

            # one label with category name
            self.labels[name] = tk.Label(self.cat_frames[name], text=name.capitalize(), width=12)
            # pack label
            self.labels[name].pack(side=tk.LEFT)

            # one input fields pre-filled with values from self.note:
            init_value = tk.StringVar(self.cat_frames[name], value=self.note[name])
            if cat_type == 'combo':
                self.inputs[name] = ttk.Combobox(self.cat_frames[name],
                                                 values=values,
                                                 state='readonly')
                # pre-select value in cbbox
                self.inputs[name].current(values.index(self.note[name]))
            else:
                if cat_type == 'text':
                    self.inputs[name] = tk.Text(self.cat_frames[name])
                    self.inputs[name].insert(tk.END, self.note[name])
                else:
                    self.inputs[name] = tk.Entry(self.cat_frames[name], textvariable=init_value, width=self.entry_width)
                # Implement select all text
                self.inputs[name].bind('<Control-KeyRelease-a>',
                                       lambda event, cat=cat_type: select_all(event, cat))
                self.inputs[name].bind('<FocusIn>',
                                       lambda event, cat=cat_type: select_all(event, cat))
            # pack input
            if name == 'one_liner':
                self.inputs[name].pack(side=tk.LEFT, expand=True, fill=tk.X)
            else:
                self.inputs[name].pack(side=tk.LEFT)
            # pack frame
            self.cat_frames[name].pack(expand=True, fill=tk.X)

    def get_values(self, name, cat_type):
        """return input in Text or Entry/combobox widgets"""
        if cat_type == 'text':
            return self.inputs[name].get(1.0, "end-1c")
        else:
            return self.inputs[name].get()

    def set_save_focus(self, *args):
        """Save if save button has focus, otherwise, focus"""
        if self.root.focus_get() == self.save_button:
            self.save_exit()
        else:
            self.save_button.focus()

    def save_exit(self):
        """save and exit"""
        self.save_note()
        self.exit_window()

    def save_note(self):
        """add note to note manager if not empty"""
        # get input values & check if not empty
        is_empty = True
        for name, cat_type, _ in self.categories:
            self.note[name] = self.get_values(name, cat_type)
            # at least one category not empty
            if is_empty:
                if self.note[name]:
                    for i in self.note[name]:
                        if i not in [' ', '\n', '\t']:
                            is_empty = False
                            break

        # save values
        if type(self.note_number) == int:
            # If editing an existing note
            if is_empty:
                # if all fields have been emptied, remove
                self.note_manager.remove_note(self.note_number)
            else:
                # otherwise, update note
                self.note_manager.update_note(self.note, self.note_number)
        else:
            if not is_empty:
                # add note
                self.note_manager.add_note(self.note)

    def delete_note(self):
        """if editing an existing note, remove it from note manager"""
        if type(self.note_number) == int:
            self.note_manager.remove_note(self.note_number)
            self.exit_window()

    def exit_window(self, *args):
        # update number of opened note windows
        self.parent.opened_note_window -= 1
        # close window
        self.root.destroy()


class SelectNote:
    def __init__(self, main):
        # options
        self.sub_categories = ['title', 'author', 'year']
        self.n_cols = len(self.sub_categories) + 1
        # width of labels/buttons
        self.max_char = 15
        self.btn_width = 4
        self.bg_color = 'green'
        self.fg_color = 'orange'
        # load var into attributes
        self.parent = main
        # window design
        self.root = tk.Toplevel(self.parent.root)
        self.root.title('Select to edit/delete')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.resizable(True, True)
        # close without saving upon hitting escape
        self.root.bind('<Escape>', func=self.exit_window)
        # Linux mouse wheel event (Up)
        self.root.bind("<Button-4>", self.mouse_wheel)
        # Linux mouse wheel event (Down)
        self.root.bind("<Button-5>", self.mouse_wheel)

        # Main frame in root
        self.frame_root = tk.Frame(self.root)
        self.frame_root.grid(sticky='news')
        # equal weight to all columns
        for i in range(self.n_cols):
            self.frame_root.grid_columnconfigure(i, weight=1)

        # create canvas for scrolling behavior
        self.canvas = tk.Canvas(self.frame_root)
        self.canvas.grid(row=1, column=0, columnspan=self.n_cols, sticky="news")
        self.canvas.grid_columnconfigure(0, weight=1)

        # allow for scrolling within the canvas
        self.vsb = tk.Scrollbar(self.frame_root, orient="vertical", command=self.canvas.yview)
        self.vsb.grid(row=1, column=self.n_cols, sticky='ns')
        self.canvas.configure(yscrollcommand=self.vsb.set)

        # Create a frame in the canvas to hold widgets
        self.frame_notes = tk.Frame(self.canvas, bg=self.bg_color)
        # equal weight to all columns
        for i in range(self.n_cols):
            self.frame_notes.grid_columnconfigure(i, weight=1)
        self.canvas.create_window((0, 0), window=self.frame_notes, anchor='nw', tags="self.frame_notes")

        # resize frame to fit canvas
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # Populate window
        self.make_titles()
        self.make_table(self.parent.note_manager)

    def make_titles(self):
        """generate column titles"""
        # generate fake button for alignment purposes
        fake_button = tk.Button(self.frame_root, text='', width=self.btn_width, state=tk.DISABLED)
        fake_button.grid(row=0, column=0, sticky='nw')
        # generate and position columns head
        for i, name in enumerate(self.sub_categories):
            label = tk.Label(self.frame_root,
                             text=name.capitalize(),
                             width=self.max_char,
                             bg=self.bg_color,
                             fg=self.fg_color
                             )
            label.grid(row=0, column=i+1, sticky='w')

    def make_table(self, note_manager):
        """populate table with info from note manager"""
        for note_number, note in enumerate(note_manager.list):
            # partial to retain number that was clicked:
            selected_note = partial(self.click, note_number)
            button = tk.Button(self.frame_notes,
                               text=str(note_number),
                               command=selected_note,
                               width=self.btn_width,
                               highlightthickness=2
                               )
            button.bind('<Return>', selected_note)
            # position button
            button.grid(row=note_number + 1, column=0, sticky='nw')

            # populate columns:
            for i, cat in enumerate(self.sub_categories):
                text = self.set_char(note[cat]).capitalize()
                label = tk.Label(self.frame_notes,
                                 text=text,
                                 width=self.max_char,
                                 bg=self.fg_color)
                # position label
                label.grid(row=note_number + 1, column=i + 1, sticky='w')

    def click(self, note_number, *args):
        """open selected note and close current window"""
        NoteWindow(self.parent, note_number=note_number)
        self.exit_window()

    def exit_window(self, *args):
        """close window"""
        # let parent know that window was closed
        self.parent.select_window = None
        self.root.destroy()

    def mouse_wheel(self, event):
        """ Mouse wheel for scrolling"""
        direction = 0
        # respond to Linux wheel event
        if event.num == 5:
            direction = 1
        if event.num == 4:
            direction = -1
        self.canvas.yview_scroll(direction, "units")

    def on_canvas_configure(self, event):
        """adjust frame to canvas and set scrolling region"""
        self.canvas.itemconfigure("self.frame_notes", width=event.width)
        # Set the canvas scrolling region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def set_char(self, string):
        """truncate strings to fit labels"""
        if len(string) > self.max_char:
            return string[:self.max_char]
        else:
            return string
