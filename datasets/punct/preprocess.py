
import re
from collections import Counter
import random
import numpy as np


valid_symbols_re = re.compile('[\w，。：！？…；、《》]')
invalid_symbols_re = re.compile('[^\w，。：！？…；、《》]')

symbols = '，。：！？…；、'
labels = 'comma, period, colon, exclamation, question, ellipsis, semicolon, pause'.split(', ')
symbol2label = dict(zip(symbols, labels))


def symbol_process(text):
    text = re.sub('\(.*?\)', '', text)
    text = re.sub('（.*?）', '', text)
    text = re.sub('[.*?]', '', text)
    text = re.sub('［.*?］', '', text)
    text = text.replace(',', '，')
    text = text.replace(':', '：')
    text = text.replace('?', '？')
    text = text.replace('!', '！')
    text = text.replace("'", '"')
    text = text.replace('‘', '"')
    text = text.replace('’', '"')
    text = text.replace('“', '"')
    text = text.replace('”', '"')
    text = text.replace('「', '"')
    text = text.replace('」', '"')
    text = text.replace('〉', '》')
    text = invalid_symbols_re.sub('', text)
    text = re.sub('\s', '', text)
    return text


def to_bmes(text):
    # text = '随即吟出一首《七绝》来：踏破白云万千重，仰天池上---水溶溶。横空大气排山去，砥柱人间是此峰。'
    # print(text)
    text = symbol_process(text)
    if len(re.findall('\w', text)) < 5:
        return ''
    res = []
    text = re.sub('(《.*?》)', ' \\1 ', text)
    for sent in text.split():
        # print(sent)
        if sent[0] == '《':
            words = re.findall('\w', sent)
            res.append('%s B-book\n' % words[0])
            if len(words) > 1:
                res += ['%s M-book\n' % w for w in words[1:-1]]
                res.append('%s E-book\n' % words[-1])
        else:
            for word, symbol in re.findall('(\w)([^\w ]?)', sent):
                if symbol:
                    res.append('%s B-%s\n' % (word, symbol2label[symbol]))
                else:
                    res.append('%s O\n' % word)
    return ''.join(res)


def generate_line(text, min_len=5, max_len=128):
    length = min_len + int((max_len - min_len) * np.random.beta(2, 6))
    # print(length)
    length = min(len(text)-1, length)
    start = random.randint(0, len(text)-length-1)
    end = start + length
    # print(text, len(text), start, end)
    if text[end].isalpha():
        text = text[start: end]
    else:
        text = text[start: end+1]
    text = re.sub('^[^《]*》', '', text)
    text = re.sub('《[^》]*$', '', text)
    return text


def count_words(text):
    return len(re.findall('\w', text))


def preprocess(infile):
    data = []
    lengths = Counter()
    with open(infile, 'r', encoding='utf8') as f:
        for line in f.readlines():
            if count_words(line) < 10:
                continue
            nsamples = int(len(line) / 50) + 1
            for _ in range(nsamples):
                subline = generate_line(line)
                lengths[len(subline)] += 1
                bmes = to_bmes(subline)
                if bmes:
                    data.append(bmes+'\n')
    print(lengths.items())
    return data


def write(train, dev, test):
    with open('train.char.bmes', 'w', encoding='utf8') as f:
        f.writelines(train)
    with open('test.char.bmes', 'w', encoding='utf8') as f:
        f.writelines(test)
    with open('dev.char.bmes', 'w', encoding='utf8') as f:
        f.writelines(dev)


def split(data):
    random.seed(0)
    random.shuffle(data)
    n = 100
    train, dev, test = data[2*n:], data[:n], data[n:2*n]
    return train, dev, test


data = preprocess('白鹿原.txt')
labels = Counter([i.split()[1] for line in data for i in line.split('\n') if i.strip()])
train, dev, test = split(data)
write(train, dev, test)

print(labels)
print(len(train), len(dev), len(test))