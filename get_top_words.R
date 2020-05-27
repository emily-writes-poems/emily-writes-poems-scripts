setwd("~/emily-writes-poems/processing/")

get_lines <- function(file_path){
    text.v <- scan(file_path, what="character", sep="\n")
    poem.title <- text.v[1]
    poem.date <- text.v[3]
    cat("=====", poem.title, "//", poem.date, "=====\n")
    return(text.v[4:length(text.v)])
}

get_words <- function(poem_lines, stopwords.v){
    words.l <- strsplit(paste(poem_lines, sep="\n", collapse=" "), "\\W")
    words.v <- unlist(words.l)
    not.blanks.v <- which(words.v != "")
    words.v <- words.v[not.blanks.v]
    words.v <- tolower(words.v)
    return(remove_stopwords(words.v, stopwords.v))
}

remove_stopwords <- function(lowercased_words, stopwords.v){
    words.v <- lowercased_words
    for(i in 1:length(stopwords.v)){
        pos.v <- which(words.v != stopwords.v[i])
        words.v <- words.v[pos.v]
    }
    return(words.v)
}

process_poem <- function(num_words, stopwords.v){
    lines.v <- get_lines(readline("Enter poem file: "))
    words.v <- get_words(lines.v, stopwords.v)
    top.words.v <- head(sort(table(words.v), decreasing=TRUE), n=num_words)
    if(top.words.v[1] == 1){
        cat("no top words")   
    } else {
        for(i in 1:length(top.words.v)){
            if(top.words.v[i] != 1){
                cat(names(top.words.v)[i], ':', top.words.v[i], '\n')
            }
        }
    }
}

stopwords.v <- scan("stopword.txt", what="character", sep="\n")
process_poem(5, stopwords.v)
