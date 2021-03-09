import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font
from tkmacosx import Button

from functools import partial

import pymongo
import config

mongo_client = pymongo.MongoClient(config.CONN_STRING)
mongo_db = mongo_client['poems']
feat_mongo_col = mongo_db['featured']
poems_feat_mongo_col = mongo_db['poems-list']


class MongoFeaturedPoemSelector:
    def __init__(self, app_root):
        self.root = app_root

    def start(self):
        self.root.title('Select a feature.')
        self.window = tk.Toplevel(self.root)
        self.frame = tk.Frame(self.window)
        self.frame.pack(expand=True)
        self.col_names = (u'\u2713',
                          'Poem ID',
                          'Poem Title',
                          'Featured Text')
        self.tree = ttk.Treeview(self.frame)
        # Data from Mongo
        self.all_featured = []
        self.all_poems = []
        self.setup()
        #self.fetch_poems()


    def setup(self):
        self.construct_frame()
        self.insert_data()
        self.window.grab_set()


    def construct_frame(self):
        # Setting up the tree's display
        self.tree["columns"] = self.col_names
        self.tree["show"] = 'headings'
        self.tree["selectmode"] = 'browse'
        tv_style = ttk.Style()
        tv_style.configure('Treeview', rowheight=25)
        self.tree.pack()

        # Columns + headings
        for i in range(len(self.col_names)):
            self.tree.column(i, anchor='c')
            self.tree.heading(f'#{i+1}', text=self.col_names[i])

        ## Set widths of columns
        self.tree.column('#1', width=30)
        self.tree.column('#2', width=150)
        self.tree.column('#3', width=150)
        self.tree.column('#4', width=600)

        # Bind double clicks on a row to expand feature data
        self.tree.bind("<Double-Button-1>", self.expand_feature_data)

        # Button that will trigger mongo update for current feature
        select_button = Button(self.frame,
                               text='Set as feature.',
                               bg='#F8F8FF',
                               fg='#5B58BB',
                               activebackground='#5B58BB',
                               borderless=1,
                               focuscolor='',
                               command=self.mongo_set_current_feature)
        select_button.pack()


    def wrap(self, string, length):
        return (string[:length] + '...') if len(string) > length else string


    def insert_data(self):
        self.mongo_get_featured_all()
        for j in range(len(self.all_featured)):
            self.tree.insert(parent='', index='end', iid=j, values=(self.all_featured[j][1],
                                                                    self.wrap(self.all_featured[j][2], 25),
                                                                    self.wrap(self.all_featured[j][3], 25),
                                                                    self.wrap(self.all_featured[j][4], 75))
                            )


    def refresh_data(self):
        self.tree.delete(*self.tree.get_children())
        self.all_featured = []
        self.insert_data()


    def expand_feature_data(self, event):
        if self.tree.selection():
            # Get double-clicked feature
            selected_row = int(self.tree.selection()[0])
            (_, _, selected_poem_id, selected_poem_title, selected_featured_text) = self.all_featured[selected_row]

            # Open new window with feature data
            window_expand_feature_data = tk.Toplevel(self.window)
            window_expand_feature_data.title('Feature for "' + selected_poem_title + '"' + ' (poem_id: ' + selected_poem_id + ')')
            window_expand_feature_data.resizable(False, False)
            window_expand_feature_data.grab_set()

            ## Create frame to hold widgets
            parent_expand_feature_data = tk.Frame(window_expand_feature_data)
            parent_expand_feature_data.pack(padx=20, pady=20)

            ## Editable text box for featured text
            text_featured_text = tk.Text(parent_expand_feature_data,
                                         width=50,
                                         height=15,
                                         font='TkDefaultFont',
                                         wrap='word')
            text_featured_text.insert('1.0', selected_featured_text)
            text_featured_text.pack(padx=20, pady=5)
            text_featured_text['state'] = 'disabled'

            ## Label for providing notification to user
            label_notification = tk.Label(parent_expand_feature_data, text='')
            label_notification.pack()


            # Buttons for edit, cancel, and save text
            def allow_edit():  # Make text editable and set focus to text box
                text_featured_text['state'] = 'normal'
                text_featured_text.focus_set()

            edit_feature_text_button = Button(parent_expand_feature_data,
                                              text='Edit text',
                                              bg='#F8F8FF',
                                              fg='#5B58BB',
                                              activebackground='#5B58BB',
                                              borderless=1,
                                              focuscolor='',
                                              command=allow_edit)
            edit_feature_text_button.pack()


            def disable_edit():  # Disable text editing and remove focus from text box
                text_featured_text['state'] = 'disabled'
                parent_expand_feature_data.focus_set()

            exit_cancel_edit_button = Button(parent_expand_feature_data,
                                             text='Cancel editing',
                                             bg='#F8F8FF',
                                             fg='#5B58BB',
                                             activebackground='#5B58BB',
                                             focuscolor='',
                                             borderless=1,
                                             command=disable_edit)
            exit_cancel_edit_button.pack()


            def notify_save_success():  # Display text in window confirming that save worked
                label_notification.config(text='Changes saved successfully.')
                label_notification.after(1500, lambda: label_notification.config(text=''))


            def save_edit():  # Save changes to Mongo, then disable text editing
                self.mongo_edit_feature_text(selected_poem_id, text_featured_text.get('1.0', 'end-1c'))
                disable_edit()
                notify_save_success()

            save_feature_text_button = Button(parent_expand_feature_data,
                                              text='Save text',
                                              bg='#F8F8FF',
                                              fg='#5B58BB',
                                              activebackground='#5B58BB',
                                              focuscolor='',
                                              borderless=1,
                                              command=save_edit)
            save_feature_text_button.pack()


            window_expand_feature_data.minsize(500, 100)
            window_expand_feature_data.mainloop()


    def mongo_get_featured_all(self):
        all_featured_raw = list(feat_mongo_col.find())
        for record in all_featured_raw:
            feature = (record['_id'],
                       u'\u2713' if record['currently_featured'] else '',
                       record['poem_id'],
                       record['poem_title'],
                       record['featured_text'])
            self.all_featured.append(feature)


    def mongo_set_current_feature(self):
        if self.tree.selection():
            # Remove current feature
            feat_mongo_col.find_one_and_update( { 'currently_featured' : True },
                                                { '$set' : { 'currently_featured' : False }  } )

            # Set selected feature
            selected_row = int(self.tree.selection()[0])
            selected_feature = self.all_featured[selected_row]
            feat_mongo_col.find_one_and_update( { '_id' : selected_feature[0] },
                                                { '$set' : { 'currently_featured' : True } } )
            self.refresh_data()


    def mongo_edit_feature_text(self, poem_id, featured_text):
        feat_mongo_col.find_one_and_update( { 'poem_id' : poem_id },
                                            { '$set' : { 'featured_text' : featured_text } } )


class MongoInsertNewFeature:
    def __init__(self, app_root):
        self.root = app_root


    def start(self):
        self.root.title('Insert new feature into database.')
        self.window = tk.Toplevel(self.root)
        self.frame = tk.Frame(self.window)
        self.frame.pack(expand=True)
        self.setup_form()
        self.window.grab_set()


    def setup_form(self):
        # Input for poem id
        poem_id_row = tk.Frame(self.frame)
        poem_id_row.pack(side=tk.TOP, padx=5, pady=5)

        poem_id_label = tk.Label(poem_id_row, text='Poem ID', anchor='w')
        poem_id_label.pack(side=tk.LEFT)

        poem_id_entry = tk.Entry(poem_id_row,
                                 font='TkDefaultFont')
        poem_id_entry.pack(side=tk.RIGHT, expand=True)

        # Input for poem title
        poem_title_row = tk.Frame(self.frame)
        poem_title_row.pack(side=tk.TOP, padx=5, pady=5)

        poem_title_label = tk.Label(poem_title_row, text='Poem Title', anchor='w')
        poem_title_label.pack(side=tk.LEFT)

        poem_title_entry = tk.Entry(poem_title_row,
                                    font='TkDefaultFont')
        poem_title_entry.pack(side=tk.RIGHT, expand=True)

        # Input textbox for feature text
        featured_text_row = tk.Frame(self.frame)
        featured_text_row.pack(side=tk.TOP, padx=5, pady=5)

        featured_text_label = tk.Label(featured_text_row, text='Featured Text', anchor='w')
        featured_text_label.pack(side=tk.LEFT)

        featured_text_textbox = tk.Text(featured_text_row,
                                        font='TkDefaultFont',
                                        height=10)
        featured_text_textbox.pack(side=tk.RIGHT, expand=True)

        # Checkbox for setting as current feature in Mongo
        set_current_feature = tk.BooleanVar()
        check_current_feature = tk.Checkbutton(self.frame, text='Set as current feature', variable=set_current_feature, onvalue=True, offvalue=False)
        check_current_feature.pack()


        def get_entries_to_insert():  # passes input values to function to insert new feature into Mongo
            self.mongo_insert_new_feature(poem_id_entry.get(), poem_title_entry.get(), featured_text_textbox.get('1.0', 'end-1c'), set_current_feature.get())

        # Submit button
        submit_button = Button(self.frame,
                               text='Submit new feature',
                               bg='#F8F8FF',
                               fg='#5B58BB',
                               activebackground='#5B58BB',
                               focuscolor='',
                               borderless=1,
                               command=get_entries_to_insert)
        submit_button.pack()


        def clear_form():  # clears all input boxes
            poem_id_entry.delete(0, 'end')
            poem_title_entry.delete(0, 'end')
            featured_text_textbox.delete('1.0', 'end')
            check_current_feature.deselect()

        # Clear form
        clear_button = Button(self.frame,
                              text='Clear',
                              bg='#F8F8FF',
                              fg='#5B58BB',
                              activebackground='#5B58BB',
                              focuscolor='',
                              borderless=1,
                              command=clear_form)
        clear_button.pack()


    def mongo_insert_new_feature(self, poem_id, poem_title, featured_text, set_current_feature):
        if not all([poem_id, poem_title, featured_text]):  # missing at least one of the required fields
            print('missing input')
            return

        feature_dict = {'poem_id' : poem_id,
                        'poem_title' : poem_title,
                        'featured_text' : featured_text}

        if set_current_feature:  # remove current feature, then insert new feature and set as current feature
            feat_mongo_col.find_one_and_update( { 'currently_featured' : True }, { '$set' : { 'currently_featured' : False }  } )
            feature_dict['currently_featured'] = True
            feat_mongo_col.insert_one(feature_dict)
        else:  # just insert new feature
            feat_mongo_col.insert_one(feature_dict)


class MongoFeatureAppController:
    def __init__(self):
        self.app_root = tk.Tk()
        default_font = tk.font.nametofont('TkDefaultFont')
        default_font.config(family='Oxygen', size=15)
        self.frame = tk.Frame()
        self.frame.pack(expand=True)
        self.FeatureSelector = MongoFeaturedPoemSelector(self.app_root)
        self.InsertNewFeature = MongoInsertNewFeature(self.app_root)
        self.setup_app()
        self.run_app()


    def add_button(self, button_text, button_command):
        new_button = Button(self.frame,
                            text=button_text,
                            bg='#F8F8FF',
                            fg='#5B58BB',
                            font=tk.font.Font(family='Oxygen', size=18),
                            activebackground='#5B58BB',
                            focuscolor='',
                            borderless=1,
                            command=button_command)
        new_button.pack(padx=25, pady=8)


    def setup_app(self):
        self.app_root.resizable(False, False)

        self.add_button("Select feature for emily-writes-poems", self.FeatureSelector.start)
        self.add_button("Create new feature for emily-writes-poems", self.InsertNewFeature.start)


    def run_app(self):
        self.app_root.mainloop()


def main():
    mongo_feature_app = MongoFeatureAppController()


if __name__ == '__main__':
    main()
