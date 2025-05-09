# About this documentation
These are notes on the MongoDB collections behind the emily-writes-poems project.


## Collections
All collections are in the `poems` database.

* `featured`
* `poem-collections-list`
* `poems-list`


### featured
The `featured` collection stores all poem features. At any time, there will be no or one document with a `true` value for the `currently_featured` field, which determines a featured poem appearing on the homepage of the site.

* `poem_id` (required): String value for poem id.
* `poem_title` (required): String value for poem title.
* `featured_text` (required): String value for the text that appears with the feature.
* `currently_featured` (required): Boolean (true/false) value as a flag for which feature is active. If the value is true, this feature will appear on the site with a link to the poem page.

### poem-collection-list
The `poem-collection-list` collection stores all poem collections, which groups up poems that have some common theme. Poems can be in multiple collections. All poem collections appear listed on the homepage of the site and are also linked on individual poem pages.

* `collection_id` (required): String value to identify the collection.
* `collection_name` (required): String value for collection title that is displayed on pages of the site.
* `collection_summary`: Optional string value that describes the collection.
* `poem_ids` (required): Array of String values for poem ids. Must be ordered to match with the `poem_titles`.
* `poem_titles` (required): Array of String values for poem titles. Must be ordered to match with the `poem_ids`.
* `wordcloud`: Document with each field mapping a word (String) to its count (Int32) across words in all poems of the collection (with a count > 2).

### poems-list
The `poems-list` collection stores all the text, details and statistics for poems. Each document is populated by 2 processes: one for the poem and one for poem details. Technically, a poem document does not require the details, but missing the details will make the poem page pretty empty.

#### Populated by processing poem
* `poem_id` (required): String value to identify the poem.
* `poem_title` (required): String value for poem title that is displayed on pages of the site.
* `poem_date` (required): String value representing when poem was written/edited.
* `poem_text` (required): Array of String values for each line of the poem. May include Markdown formatting. A value of an empty string ("") indicates a empty line, usually separating stanzas.
* `poem_linecount` (required): Int32 value for number of lines, including empty lines (usually used to separate stanzas).
* `poem_wordcount` (required): Int32 value for number of words.
##### Populated by similar poems script (called when processing poem)
The similar poems script is run on an entire directory of poem files.
* `similar_poems_ids` (required): Array of String values for poem ids. Must be ordered to match with the `similar_poems_titles`.
* `similar_poems_titles` (required): Array of String values for poem ids. Must be ordered to match with the `similar_poems_ids`.
#### Populated by processing poem details
* `poem_behind_title` (required): String value for information about how the poem's title came to be. May include Markdown formatting.
* `poem_behind_poem` (required): String value for information about inspiration and writing process for the poem. May include Markdown formatting.
* `top_words`: Document with each field mapping a word (String) to its count (Int32) in the poem.
