# Title     : TODO
# Objective : TODO
# Created by: kimjiwoo
# Created on: 2021-08-13


install.packages("readxl")
install.packages("udpipe")
install.packages("textrank")
install.packages("lattice")
install.packages("tm")
install.packages("wordcloud")
install.packages("igraph")
install.packages("ggraph")
install.packages("ggplot2")

library(udpipe)
library(textrank)
library(lattice)
library(wordcloud)
library(readxl)
library(Rcpp)
library(tm)
library(igraph)
library(ggraph)
library(ggplot2)

setwd("C:/Users/") # 워킹 디렉토리로 설정해 주세요!!!!


#load analysis model
ud_model <- udpipe_download_model(language="english")
ud_model <- udpipe_load_model(ud_model)


# test only one file
articles <- c()
tmp <- read_excel("C:/Users/kimjiwoo/Desktop/crawl_R/LATimes(2019).xlsx")["article"] # 파일 하나만 읽는 버전
for (article in tmp){
  articles <- append(articles, tolower(article))
}
articles <- unique(articles)

##################################################################################### 파일 여러개 읽는 버전
# read articles from excels
# for(year in 2010:2020){
#  tmp <- read_excel(paste0("LATimes(", as.character(year), ").xlsx"))["article"]
#  for (article in tmp){
#    articles<-append(articles, tolower(article))
#  }
# }
# articles <- unique(articles)
#####################################################################################



# make corpus
corpus <- Corpus(VectorSource(articles))


# customize stopwords # stopwords들 추가는 여기다가 해주세요!!
customizedStopwords <- c("kim", "time", "'s", "'re", "p.m", "a.m", "p.m.", "year","years", "a.m.", "pm", "am", "korea", "thing", "mon", "tue", "wed", "thu", "fri", "sat", "la")

# preprocess corpus
## 1. 숫자 제거
preproCorpus <- tm_map(corpus, removeNumbers)
## 2. 불용어 제거
preproCorpus <- tm_map(preproCorpus, removeWords, c(stopwords("en"), customizedStopwords, "Top200Words"))
# preproCorpus <- tm_map(preproCorpus, removeWords, customizedStopwords)
# preproCorpus <- tm_map(preproCorpus, removeWords, "Top200Words")
## 3. 문장부호 제거
preproCorpus <- tm_map(preproCorpus, removePunctuation)

# corpus to list
preprocArticles <- sapply(preproCorpus, as.character)
preprocArticles
# analyze articles
x <- udpipe_annotate(ud_model, preprocArticles)
x <- as.data.frame(x)
## x$lemma ===> 표제어 추출까지 완료된 단어들의 집합
## x$upos ===> 표제어 추출이 완료된 단어들의 품사


# get subset of words only composed with noun
stats <- subset(x, upos %in% "NOUN") # subset(x, upos %in% c("NOUN", "ADJ", .. ))로 응용 가능
stats <- txt_freq(x = stats$lemma)

# wordcloud
pal <- brewer.pal(8, "Dark2")
wordcloud(words= stats$key, freq=stats$freq, min.freq = 10, random.order = F, max.words=150, colors=pal, scale=c(4, 0.3))

# bar plot (빈도)
stats$key <- factor(stats$key, levels=rev(stats$key))
barchart(key ~ freq, data = head(stats, 30), col = "cadetblue", main="Most occurring nouns", xlab = "Freq")

# co-occurrence & collocation
collocation <- keywords_collocation(x = x, term="token", group=c("doc_id", "paragraph_id", "sentence_id"), ngram_max = 4)
cooc <- cooccurrence(x = subset(x, upos %in% c("NOUN", "ADJ")), term="lemma", group=c("doc_id", "paragraph_id", "sentence_id"))
cooc <- cooccurrence(x = x$lemma, relevant = x$upos %in% c("NOUN", "ADJ"))

# draw graph
wordnetwork <- head(cooc, 50)
wordnetwork
wordnetwork <- graph_from_data_frame(wordnetwork)
ggraph(wordnetwork, layout="fr") +
  geom_edge_link(aes(width=cooc, edge_alpha=cooc), edge_colour = "pink") +
  geom_node_text(aes(label = name), col="darkgreen", size=4) +
  theme_graph(base_family = "Calibri") +
  theme(legend.position="none") +
  labs(title = "Cooccurrences within 3 words distance", subtitle = "Noun & Adjective")

#
