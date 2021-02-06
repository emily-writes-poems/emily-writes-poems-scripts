import tkinter as tk
import tkinter.ttk as ttk

from functools import partial

import pymongo
import config

mongo_client = pymongo.MongoClient(config.CONN_STRING)
mongo_db = mongo_client['poems']
mongo_col = mongo_db['featured']


class MongoFeaturedPoemSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.col_names = ('Currently featured', 'Poem ID', 'Poem Title', 'Featured Text')
        self.tree = ttk.Treeview(self.root)
        self.all_featured = []
        self.setup_tree()
        self.root.mainloop()

    def setup_tree(self):
        self.construct_tree()
        self.insert_data()

    def construct_tree(self):
        self.root.title('Select a feature.')
        self.tree["columns"] = self.col_names
        self.tree["show"] = 'headings'
        self.tree["selectmode"] = 'browse'
        self.tree.pack()

        # Columns + headings
        for i in range(len(self.col_names)):
            self.tree.column(i, anchor='c')
            self.tree.heading(f'#{i+1}', text=self.col_names[i])

        self.tree.column('#1', width=140)
        self.tree.column('#4', width=350)

        # Button that will trigger mongo update
        select_button = tk.Button(self.root, text="Set as feature.", command=self.mongo_set_feature)
        select_button.pack()

    def mongo_get_featured_all(self):
        all_featured_raw = list(mongo_col.find())
        for record in all_featured_raw:
            feature = (record['_id'], record['currently_featured'], record['poem_id'], record['poem_title'], record['featured_text'])
            self.all_featured.append(feature)

    def wrap(self, string, length=40):
        return (string[:length] + '...') if len(string) > length else string

    def insert_data(self):
        self.mongo_get_featured_all()
        for j in range(len(self.all_featured)):
            self.tree.insert(parent='', index='end', iid=j, values=(self.all_featured[j][1], self.all_featured[j][2], self.all_featured[j][3], self.wrap(self.all_featured[j][4])))

    def refresh_data(self):
        self.tree.delete(*self.tree.get_children())
        self.all_featured = []
        self.insert_data()

    def mongo_set_feature(self):
        # Remove current feature
        mongo_col.find_one_and_update( { 'currently_featured' : True }, { '$set' : { 'currently_featured' : False }  } )
        # Set selected feature
        selected_row = int(self.tree.selection()[0])
        selected_feature = self.all_featured[selected_row]
        mongo_col.find_one_and_update( { '_id' : selected_feature[0] }, { '$set' : { 'currently_featured' : True } } )
        self.refresh_data()


def main():
    FeatureSelector = MongoFeaturedPoemSelector()

if __name__ == '__main__':
    main()
