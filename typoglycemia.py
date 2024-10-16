# -*- coding: utf-8 -*-
"""Typoglycemia.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1LP8nOk4_xopXPl9B8UGAt1bvaYgoMa6S

levenshteinモジュールのインストール
"""

!pip install levenshtein

"""distance関数のテスト"""

from Levenshtein import distance
distance("The quick brown fox jumps over the lazy dog", "The qiuck brwon fox jupms oevr the lzay dog")

"""TL指標の定義"""

def tl(s1:str, s2:str) -> float:
  return distance(s1, s2) / len(s1)

"""TL関数のテスト"""

tl("The quick brown fox jumps over the lazy dog", "The qiuck brwon fox jupms oevr the lzay dog")

"""テストデータとして長めのものを用意する"""

orig:str = "こんにちは みなさん おげんき ですか わたしは げんき です 。\
この ぶんしょう は いぎりす の ケンブリッジ だいがく の けんきゅう の けっか \
にんげん は もじ を にんしき する とき その さいしょ と さいご の もじさえ あっていれば \
じゅんばん は めちゃくちゃ でも ちゃんと よめる という けんきゅう に もとづいて \
わざと もじの じゅんばん を いれかえて あります 。 \
どうです ？ よめちゃう でしょ ？"

"""文字を一つ入れ替える関数swapの定義（入れ替えられなかったらNoneを返す）"""

import random

def swap(s:str) -> str:
  words:list[str] = s.split()
  candidates:list[str] = list(filter(lambda x: len(x) > 3, words))

  # return None if the string has no words that have more than four letters
  if len(candidates) == 0:
    return None

  # swopword: target word for swapping two internal characters
  swapword:str = candidates[random.randint(0, len(candidates) - 1)]

  # targetidx: target position for swapping characters
  targetidx:int = random.randint(1, len(swapword) - 3)

  # swapped: the word whose internal characters are swapped
  swapped:str = swapword[:targetidx] \
              + swapword[targetidx + 1] + swapword[targetidx] \
              + swapword[targetidx + 2:]

  #  replace the target word with swapped word, and returnds the sentence
  words[words.index(swapword)] = swapped
  return " ".join(words)

"""入れ替えのテスト"""

swap("The quick brown fox jumps over the lazy dog")

"""tl値を指定してそれ以上になるまで入れ替えを繰り返す関数を定義する（iter回試してtl値を超えられなかったらNoneを返す. iterのデフォルト値は1000とする）"""

def typoglycemia(orig:str, tlval:float, iter:int=1000) -> str:
  typo:str = swap(orig)

  # iterate swapping iter times
  # return the swapped text if the value of tl ecceeds tlval
  for i in range(iter):
    if tl(orig, typo) >= tlval: return typo
    typo = swap(typo)

  # the case that the trial was failed.
  return None

"""テスト"""

typoglycemia(orig, 0.20)

"""TLを再定義しswap可能な単語のうち少しでもswapされている単語の比率でTLを定義しなおす"""

def tl(s1:str, s2:str) -> float:
  s1_targets:list[str] = list(filter(lambda x: len(x) > 3, s1.split()))
  s2_targets:list[str] = list(filter(lambda x: len(x) > 3, s2.split()))

  # count the number of the swapped words
  ctr:int = 0
  for i in range(len(s1_targets)):
    if distance(s1_targets[i], s2_targets[i]) > 0: ctr += 1

  # this function returns the ratio of the swapped words
  return ctr / len(s1_targets)

"""再定義したTL関数を利用したものでのテスト"""

typoglycemia(orig, 0.90)

"""ランダムに抽出してswapを繰り返す方法だと100%は難しいので，比率を指定して対象の単語を定める方法に変えてみる"""

def typoglycemia(orig:str, tlval:float) -> str:
  indexes:list[int] = []
  s_words:list[str] = orig.split()

  # candidates are the list contains swappable words.
  for i in range(len(s_words)):
    if len(s_words[i]) > 3: indexes.append(i)

  # shuffle the indexes and define the scope of swapping characters
  random.shuffle(indexes)
  target_idx:list[int] = indexes[:int(len(indexes) * tlval)]

  # swap the target
  for i in target_idx:
    s_words[i] = swap(s_words[i]) # this code should be refactored!!!

  return " ".join(s_words)

"""これだと100%の入れ替えも実現可能

テスト（tl値1.0を指定したケース）
"""

typoglycemia(orig, 1.0)

"""テスト（tl値0.2を指定したケース）"""

typoglycemia(orig, 0.20)

"""さらに発展させると, 変更できる文字の数の割合でTLを定めるというものも定義できよう. すなわち, "The quick brown fox jumps over ..." という文であれば，入れ替え可能な文字は"@@@ @uick@ @row@ @@@ @ump@ @ve@ ..." のアットマークで消されていない部分なので, その部分の入れ替え対象の割合を0.0から1.0の間で指定すればよいということである. 単語内部の文字の入れ替えは, 同じ位置にならないようにうまく入れ替えるのは難しいので, とりあえず, 2文字ずつ交換していき, 単語のなかでの候補となる文字が3つになったらabc→bcaとなるようローテーションさせればよいということにしよう.

なお「あああああ」みたいな単語はいくら交換しても「あああああ」以外に変換し得ないので, 同じ文字を入れ替えて変化がないケースは無視し, そのような入れ替え操作も変換回数に数えるものとする.
"""

# the definition of the function that makes the array of array
# indicating the candidate character positions
def make_candidate_index(orig:str, debug:bool=False) -> list[list[int]]:
  tmp:str = " "
  candidate:str = " "
  stopwords:str = " ,.!?！？．。，、「」\"\#\*\&\n"
  indexes:list[int] = []

  # see how the code runs by setting the debug=True flag
  if debug: print("ORG:" + orig)
  for i in range(1, len(orig)-1):
    tmp = tmp[:i] + (" " \
          if orig[i-1] in stopwords or orig[i+1] in stopwords \
             or orig[i] in stopwords else orig[i])
  if debug: print("TMP:" + tmp)
  for i in range(1, len(tmp)-1):
    candidate = candidate[:i] + (" " \
          if (tmp[i-1] in stopwords and tmp[i+1] in stopwords) \
             or (tmp[i] in stopwords) else tmp[i])
  if debug: print("CDD:" + candidate)
  flag:bool = False
  for i in range(1, len(candidate)-1):
    if candidate[i] not in stopwords:
      if not flag: flag = True; subindexes = [i]
      else: subindexes.append(i)
    else:
      if flag: indexes.append(subindexes)
      flag = False
  return indexes

"""その関数のテスト（debug=Trueでデバッグプリントを出力）

ORG: 元のテキスト

TMP: 左右にストップワードが含まれるような単語は空白と入れ替え

CDD: 孤立している文字は空白と入れ替え
"""

make_candidate_index("The quick brown superpowered fox hyperjumps over the beautiful lazy dog.", debug=True)

"""これを利用してTL値を満たすまでの入れ替えを行う関数を定義する."""

from functools import reduce

def typoglycemia(orig:str, tlval:float, debug=False) -> str:
  if tlval < 0.0 or tlval > 1.0:
    print("tlval must be between 0.0 and 1.0")
    return None

  # firstly, make the index array
  indexes:list[list[int]] = make_candidate_index(orig)

  # count the number of the items in the array 'indexes'
  denominator:int = len(reduce(lambda x, y: x+y, indexes))

  # the list of swapping or rotating characters
  procs:list[list[int]] = []
  # the number of swapped characters
  swap_nums:int = 0

  while swap_nums < tlval * denominator:
    # find the target item
    target_idx:int = random.randint(0, len(indexes) - 1)
    target_list = indexes[target_idx]
    if debug: print("---\ntarget: " + str(target_list))

    # pop the two characters if the word is long enough
    if len(target_list) >= 4:
      char_idx:int = 0
      swap_idx:int = 0
      while char_idx == swap_idx:
        char_idx = random.randint(0, len(target_list) - 1)
        swap_idx = random.randint(0, len(target_list) - 1)
      c1 = target_list[char_idx]
      c2 = target_list[swap_idx]
      target_list.remove(c1)
      target_list.remove(c2)
      procs.append([c1, c2])
      swap_nums += 2

    # the case if the word length is two or three
    elif len(target_list) == 2 or len(target_list) == 3:
      procs.append(target_list)
      indexes.remove(target_list)
      swap_nums += len(target_list)

    else:
      print("error")
      return None

    if debug:
      print("swap_num: " + str(swap_nums))
      print("procs: " + str(procs))
      print("processed target: " + str(target_list))

  if debug: print("residue:" + str(indexes))

  # swap or rotate characters according to the list procs
  chars:list[str] = list(orig)
  for l in procs:
    if len(l) == 2:
      tmp:str = chars[l[0]]
      chars[l[0]] = orig[l[1]]
      chars[l[1]] = tmp
    else:
      tmp:str = chars[l[0]]
      if random.randint(0, 1) == 0: # rotate clockwise or ...
        chars[l[0]] = orig[l[1]]
        chars[l[1]] = orig[l[2]]
        chars[l[2]] = tmp
      else:                         # rotate counter-clockwise
        chars[l[0]] = orig[l[2]]
        chars[l[2]] = orig[l[1]]
        chars[l[1]] = tmp

  return "".join(chars)

"""テスト"""

typoglycemia("The superpowered quick brown fox jumps over the beautiful lazy dog.", 0.8, debug=False)

"""日本語のサンプルでテスト"""

tgc = typoglycemia(orig, 1.0)
tgc

"""変換対象となる文字列の範囲でタイポグリセミア度を計測する関数tlを再定義する"""

def tl(s1:str, s2:str) -> float:
  s1_words:list[str] = [x[1:-1] for x in filter(lambda x: len(x) > 3, s1.split())]
  s2_words:list[str] = [x[1:-1] for x in filter(lambda x: len(x) > 3, s2.split())]
  s1_chars:list[str] = list("".join(s1_words))
  s2_chars:list[str] = list("".join(s2_words))
  ctr:int = 0

  for i in range(len(s1_chars)):
    if s1_chars[i] != s2_chars[i]: ctr += 1

  return ctr / len(s1_chars)

"""確認（tl = 1.0として指定したものだとしても, 同じ文字がスワップされるケースがあるので1.0を下回る場合があり得る）"""

tl(tgc, orig)