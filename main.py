# pip install gensim
# pip install janome

from lib2to3.pgen2 import token
from urllib import request
import requests
from bs4 import BeautifulSoup
from janome.tokenizer import Tokenizer
from gensim.models import word2vec
import time
import re

starttime = time.time()

def tokenize(text, t = Tokenizer()):
    tokens = t.tokenize(text)
    word = []
    stop_word = create_stop_word()
    for token in tokens:
        part_of_speech = token.part_of_speech.split(",")[0]
        if part_of_speech in ['名詞', '動詞', '形容詞', '形容動詞'] and token.base_form not in stop_word:
            word.append(token.base_form)

    return word

def create_stop_word():
    target_url = "http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt"
    r = requests.get(target_url)
    soup = BeautifulSoup(r.text, "html.parser")
    stop_word = str(soup).split()

    stop_word.extend([i for i in "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"])
    stop_word.extend(["れる", "なる", "ひる", "つて", "てる"])

    return stop_word

base_url = "https://www.uta-net.com/"
result_search_url = "https://www.uta-net.com/search/?target=art&type=in&Keyword=%E6%A4%8E%E5%90%8D%E6%9E%97%E6%AA%8E"

res = requests.get(result_search_url)
soup = BeautifulSoup(res.text, "html.parser")

singer_list = [h.get("href") for h in soup.find_all("a", attrs={"class": "d-block"})]
singer_list.extend(["/artist/3484/"])

kashi_list = []
for u in singer_list:
    res = requests.get(base_url + u)
    soup = BeautifulSoup(res.text, "html.parser")

    for song in soup.find_all("span", attrs={"class": "d-block d-lg-none utaidashi text-truncate"}):
        kashi = song.string.replace("\u3000", " ")
        
        # 英数字の削除
        kashi = re.sub("[a-zA-Z0-9_]","",kashi)
        # 記号の削除
        kashi = re.sub("[!-/:-@[-`{-~]","",kashi)
        # 空白・改行の削除
        kashi = re.sub(u'\n\n', '\n', kashi)
        kashi = re.sub(u'\r', '', kashi)

        kashi = kashi.strip()
        kashi_list.append(kashi)

print('len :', len(kashi_list))
sentence = [tokenize(i) for i in kashi_list]

model = word2vec.Word2Vec(sentence, min_count=4, window=15)
for i in model.wv.most_similar(positive=["人生"], topn=40):
    # 長い単語を出したい時は下の行をコメント解除してtopn=200くらいにした
    # if len(i[0]) > 2:
    print(round(i[1], 8), i[0])

print('time :', time.time() - starttime)