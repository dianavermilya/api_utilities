import os
import json
import indicoio
import operator

indicoio.config.api_key = os.get_env(INDICO_API_KEY)


def load_data(filename):
    with open(filename, 'rb') as f:
        return [json.loads(l) for l in f]


def dump_data(filename, data):
    with open(filename, 'wb') as outfile:
        json.dump(data, outfile)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def sample():
    data = load_data('/Users/diana/articles_for_diana.ndjson')
        for i in range(150):
        l = data[i]['text'].split("\n")
        l = filter(lambda x: x!="", l)
        try:
            print l[0]
        except: 
            pass
        w = ".".join(data[100*i]['content'].split(".")[3:7])+"."
        print w.replace("\n", " ")

sample()



def filter_for_english():
    data = load_data('/Users/diana/medium_top_10k_hearts.ndjson')
    return_data = []
    for chunk in chunks(data, 100):
        article_texts = [article['content'] for article in chunk]
        languages = [d.keys()[0] for d in indicoio.language(article_texts, top_n=1)]
        for i in range(len(chunk)):
            if languages[i] == 'English':
                return_data.append(chunk[i])

    return_data = [x for x in return_data if len(x['content']) > 2500]
    dump_data('articles.ndjson', return_data)


def indico_data(data):
    data = load_data('/Users/diana/articles.ndjson')
    for chunk in chunks(data, 100):
        article_texts = [article['content'] for article in chunk]
        sentiment = indicoio.sentiment(article_texts, top_n=1)
        text_tags = [sorted(d.items(), key=operator.itemgetter(1)) for d in indicoio.text_tags(article_texts, top_n=5)]
        political = [sorted(d.keys(), key=operator.itemgetter(1)) for d in indicoio.political(article_texts, top_n=3)]
        for i in range(len(chunk)):
            article = chunk[i]
            article['sentiment'] = sentiment[i]
            article['text_tags'] = text_tags[i]
            article['political'] = political[i]

    with open('indicoed_articles.ndjson', 'wb') as outfile:
        json.dump(data, outfile)


def score_by_tag_match(article, interests):
    score = 0
    for article_tag in article['text_tags']:
        for interest_tag in interests:
            if article_tag[0] == interest_tag[0]:
                score += article_tag[1] * interest_tag[1]
    return score


def choose_articles(interests):
    data = load_data('/Users/diana/indicoed_articles.ndjson')[0]
    sorted_by_score = sorted(data, key=lambda x: score_by_tag_match(x, interests), reverse=True)
    del sorted_by_score[10:]
    return sorted_by_score


def get_tags(text):
    tag_dict = indicoio.text_tags(text)
    sorted_tags = sorted(tag_dict.items(), key=lambda tup: -tup[1])[:5]
    return sorted_tags


def recommend():
    tags = get_tags("The painting doesn't capture the same sadness.")
    articles = choose_articles(tags)
    titles = map(lambda x: x['title'], articles)
    print titles
    return articles
