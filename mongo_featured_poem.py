import tkinter as tk
import tkinter.ttk as ttk

from functools import partial

import pymongo
import config

mongo_client = pymongo.MongoClient(config.CONN_STRING)
mongo_db = mongo_client['poems']
mongo_col = mongo_db['featured']


class MongoFeaturedPoemSelector:
    def __init__(self, app_root):
        self.root = app_root
        self.frame = tk.Frame(self.root)
        self.frame.title('Select a feature.')
        self.frame.pack(expand=True)
        self.col_names = (u'\u2713',
                          'Poem ID',
                          'Poem Title',
                          'Featured Text')
        self.tree = ttk.Treeview(self.frame)
        self.all_featured = []
        self.setup_tree()


    def destroy(self):
        self.frame.destroy()


    def setup_tree(self):
        self.construct_tree()
        self.insert_data()


    def construct_tree(self):
        self.tree["columns"] = self.col_names
        self.tree["show"] = 'headings'
        self.tree["selectmode"] = 'browse'
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

        # Button that will trigger mongo update for current feature
        select_button = tk.Button(self.frame, text="Set as feature.", command=self.mongo_set_feature)
        select_button.pack()

        # Bind double clicks on a row to expand feature data
        self.tree.bind("<Double-Button-1>", self.expand_feature_data)


    def wrap(self, string, length):
        return (string[:length] + '...') if len(string) > length else string


    def insert_data(self):
        self.mongo_get_featured_all()
        for j in range(len(self.all_featured)):
            self.tree.insert(parent='', index='end', iid=j, values=(self.all_featured[j][1],
                                                                    self.wrap(self.all_featured[j][2], 30),
                                                                    self.wrap(self.all_featured[j][3], 30),
                                                                    self.wrap(self.all_featured[j][4], 85))
                            )


    def refresh_data(self):
        self.tree.delete(*self.tree.get_children())
        self.all_featured = []
        self.insert_data()


    def expand_feature_data(self, event):
        if self.tree.selection():
            # Get double-clicked feature
            selected_row = int(self.tree.selection()[0])
            selected_feature = self.all_featured[selected_row]
            # Open new window with feature data
            window_expand_feature_data = tk.Toplevel(self.root)
            window_expand_feature_data.title('Feature for "' + selected_feature[2] + '"')

            parent_expand_feature_data = tk.Frame(window_expand_feature_data)
            parent_expand_feature_data.pack(expand=True)

            label_feature_text = tk.Label(parent_expand_feature_data, text = selected_feature[4], wraplength=500)
            label_feature_text.pack(padx=(20,20))

            window_expand_feature_data.minsize(500, 100)
            window_expand_feature_data.mainloop()


    def mongo_get_featured_all(self):
        all_featured_raw = list(mongo_col.find())
        for record in all_featured_raw:
            feature = (record['_id'],
                       u'\u2713' if record['currently_featured'] else '',
                       record['poem_id'],
                       record['poem_title'],
                       record['featured_text'])
            self.all_featured.append(feature)


    def mongo_set_feature(self):
        if self.tree.selection():
            # Remove current feature
            mongo_col.find_one_and_update( { 'currently_featured' : True }, { '$set' : { 'currently_featured' : False }  } )
            # Set selected feature
            selected_row = int(self.tree.selection()[0])
            selected_feature = self.all_featured[selected_row]
            mongo_col.find_one_and_update( { '_id' : selected_feature[0] }, { '$set' : { 'currently_featured' : True } } )
            self.refresh_data()


class MongoInsertNewFeature:
    def __init__(self, app_root):
        self.root = app_root
        self.frame = tk.Frame(self.root)
        self.root.title('Insert new feature into database.')
        self.frame.pack(expand=True)
        self.create_form()


    def destroy(self):
        self.frame.destroy()


    def create_form(self):
        # Input for poem id
        poem_id_row = tk.Frame(self.frame)
        poem_id_row.pack(side=tk.TOP, padx=5, pady=5)
        poem_id_label = tk.Label(poem_id_row, text='Poem ID', anchor='w')
        poem_id_label.pack(side=tk.LEFT)
        poem_id_entry = tk.Entry(poem_id_row)
        poem_id_entry.pack(side=tk.RIGHT, expand=True)

        # Input for poem title
        poem_title_row = tk.Frame(self.frame)
        poem_title_row.pack(side=tk.TOP, padx=5, pady=5)
        poem_title_label = tk.Label(poem_title_row, text='Poem Title', anchor='w')
        poem_title_label.pack(side=tk.LEFT)
        poem_title_entry = tk.Entry(poem_title_row)
        poem_title_entry.pack(side=tk.RIGHT, expand=True)

        # Input textbox for feature text
        feature_text_row = tk.Frame(self.frame)
        feature_text_row.pack(side=tk.TOP, padx=5, pady=5)
        feature_text_label = tk.Label(feature_text_row, text='Featured Text', anchor='w')
        feature_text_label.pack(side=tk.LEFT)
        feature_text_textbox = tk.Text(feature_text_row, height=10)
        feature_text_textbox.pack(side=tk.RIGHT, expand=True)

        # Checkbox for setting as current feature in Mongo
        set_feature = False
        check_current_feature = tk.Checkbutton(self.frame, text='Set as current feature', variable=set_feature, onvalue=True, offvalue=False)
        check_current_feature.pack()


        def get_entries_to_insert():
            self.mongo_insert_new_feature(poem_id_entry.get(), poem_title_entry.get(), feature_text_textbox.get('1.0', 'end-1c'), set_feature)

        # Submit button
        submit_button = tk.Button(self.frame, text='Submit new feature', command=get_entries_to_insert)
        submit_button.pack()


        def clear_form():
            poem_id_entry.delete(0, 'end')
            poem_title_entry.delete(0, 'end')
            feature_text_textbox.delete('1.0', 'end')
            check_current_feature.deselect()

        # Clear form
        clear_button = tk.Button(self.frame, text='Clear', command=clear_form)
        clear_button.pack()


    def mongo_insert_new_feature(self, poem_id, poem_title, feature_text, set_feature):
        print (poem_id, poem_title, feature_text, set_feature)


def main():
    app_root = tk.Tk()
    #FeatureSelector = MongoFeaturedPoemSelector(app_root)
    InsertNewFeature = MongoInsertNewFeature(app_root)
    app_root.mainloop()


if __name__ == '__main__':
    main()
