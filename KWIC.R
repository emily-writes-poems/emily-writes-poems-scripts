get_lines <- function(file_path){
    text.v <- scan(file_path, what="character", sep="\n")
    poem.title <- text.v[1]
    poem.date <- text.v[3]
    cat("=====", poem.title, "//", poem.date, "=====\n")
    return(text.v[4:length(text.v)])
}

get_words <- function(poem_lines){
    words.l <- strsplit(paste(poem_lines, sep="\n", collapse=" "), "\\W")
    words.v <- unlist(words.l)
    not.blanks.v <- which(words.v != "")
    words.v <- words.v[not.blanks.v]
    words.v <- tolower(words.v)
    return(words.v)
}

process_poem <- function(){
    lines.v <- get_lines(readline("Enter poem file: "))
    words.v <- get_words(lines.v)
    top.words.v <- head(sort(table(words.v), decreasing=TRUE), n=10)
    cat("TOP 10 WORDS\n")
    print(top.words.v)
    return(words.v)
}

poem.v <- process_poem()
