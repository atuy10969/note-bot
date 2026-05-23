import anthropic
import datetime
import json
import os
from config import ANTHROPIC_API_KEY

# ============================================================
# 就活RPG：レベルアップロードマップ
# 読者が1から読み進めると就活初心者→内定レベルに成長する
# ============================================================

INTERN_TOPICS = [
    # Lv.1 入門編
    {
        "level": "Lv.1 入門編",
        "title": "サマーインターンって何？大学3年生が最初に知るべき基礎知識",
        "angle": "インターンシップの定義・種類・目的をゼロから解説。参加したことがない人でも全体像がわかるように"
    },
    {
        "level": "Lv.1 入門編",
        "title": "就活のスケジュール、いつから動けばいい？全体像を解説",
        "angle": "大学3年の春〜4年の内定までの流れを時系列で解説。何月に何をすべきか逆算で示す"
    },
    {
        "level": "Lv.1 入門編",
        "title": "インターンに参加するメリット、正直に話す",
        "angle": "建前ではなくリアルなメリットを語る。早期選考・内定直結・業界理解など実体験ベースで"
    },

    # Lv.2 準備編
    {
        "level": "Lv.2 準備編",
        "title": "自己分析って何をするの？就活初心者向けに超シンプルに解説",
        "angle": "自己分析の目的と最低限やるべきことをシンプルに。難しく考えすぎている人へ"
    },
    {
        "level": "Lv.2 準備編",
        "title": "自己分析の結果をESに変換する方法",
        "angle": "自己分析はしたけどESに書けない人向け。分析→言語化→ES記述の流れを具体的に"
    },
    {
        "level": "Lv.2 準備編",
        "title": "業界研究の始め方、何から調べればいい？",
        "angle": "業界研究のやり方がわからない初心者向け。効率的な情報収集の手順を解説"
    },
    {
        "level": "Lv.2 準備編",
        "title": "金融業界って何？理系でも目指せる理由",
        "angle": "金融＝文系というイメージを覆す。理系スキルが金融で活きる理由を実体験で語る"
    },

    # Lv.3 応募編
    {
        "level": "Lv.3 応募編",
        "title": "インターンのESって何を書くの？初心者向けに解説",
        "angle": "ESの構成・各設問の意図・書き方の基本をゼロから説明"
    },
    {
        "level": "Lv.3 応募編",
        "title": "ガクチカの作り方、ネタがないと思ってる人へ",
        "angle": "研究・バイト・サークルなど平凡な経験からガクチカを作る方法。ネタがなくても書ける"
    },
    {
        "level": "Lv.3 応募編",
        "title": "逆求人サービスとは？待つだけでスカウトが来る仕組み",
        "angle": "逆求人の仕組みをわかりやすく解説。学歴フィルター回避の最強武器として紹介"
    },
    {
        "level": "Lv.3 応募編",
        "title": "OfferBoxとキミスカ、どっちを使うべき？実際に両方使った感想",
        "angle": "2つの逆求人サービスを比較。どんな人にどちらが向いているか実体験で語る"
    },

    # Lv.4 選考編
    {
        "level": "Lv.4 選考編",
        "title": "インターン面接で聞かれること TOP5、対策も解説",
        "angle": "頻出質問とその答え方のコツを具体的に。実際に聞かれた質問をベースに"
    },
    {
        "level": "Lv.4 選考編",
        "title": "学歴フィルターって本当にあるの？実際に食らった話",
        "angle": "フィルターの実態を正直に語る。存在を認めつつ回避策を提示する"
    },
    {
        "level": "Lv.4 選考編",
        "title": "グループワークで評価される立ち回り方",
        "angle": "GWで埋もれない方法。役割の取り方・発言のタイミング・評価されるポイント"
    },
    {
        "level": "Lv.4 選考編",
        "title": "OB訪問の始め方、ゼロから解説",
        "angle": "OB訪問が怖い・やり方わからない人向け。Matcherの使い方・メッセージ文まで"
    },
    {
        "level": "Lv.4 選考編",
        "title": "OB訪問で絶対に聞くべき質問、ネットには載ってないやつ",
        "angle": "表面的でない本音を引き出す質問集。OB訪問を最大限活用する方法"
    },

    # Lv.5 実践編
    {
        "level": "Lv.5 実践編",
        "title": "インターン当日にやること・持ち物リスト",
        "angle": "初めてインターンに参加する人向け。当日の流れと準備すべきことを具体的に"
    },
    {
        "level": "Lv.5 実践編",
        "title": "金融インターンの1日の流れ、リアルを話す",
        "angle": "実際に参加した金融インターンの当日レポート。雰囲気・内容・参加者層を正直に"
    },
    {
        "level": "Lv.5 実践編",
        "title": "インターンで失敗した話と、そこから学んだこと",
        "angle": "失敗談を正直に語る。緊張・準備不足・グループワークの失敗など等身大のリアル"
    },
    {
        "level": "Lv.5 実践編",
        "title": "旧帝大・早慶だらけの選考会場で、4工大の僕が感じたこと",
        "angle": "周囲と学歴差を感じた瞬間のリアルな気持ち。そこからどう立て直したか"
    },

    # Lv.6 次のステップ
    {
        "level": "Lv.6 次のステップ",
        "title": "インターンから本選考につなげる方法",
        "angle": "インターン参加後にやるべきこと。お礼・振り返り・本選考への活かし方"
    },
    {
        "level": "Lv.6 次のステップ",
        "title": "早期選考って何？インターン参加者だけの特別ルート",
        "angle": "早期選考の仕組みと、インターンがなぜ重要かをつなげて解説"
    },
    {
        "level": "Lv.6 次のステップ",
        "title": "4工大から大手金融に内定できた理由、全部話す",
        "angle": "選考フロー・対策・意識したことを全部公開。学歴より大事だったものを語る"
    },
    {
        "level": "Lv.6 次のステップ",
        "title": "就活を終えて思うこと、後輩へのメッセージ",
        "angle": "就活全体を振り返って伝えたいこと。学歴コンプがあった自分が言える言葉で締める"
    },
]

# カウンターファイルのパス
COUNTER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "article_counter.json")


def get_next_topic():
    """次に投稿するトピックを返す（順番通りに進む）"""
    # カウンターを読み込む
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        index = data.get("index", 0)
    else:
        index = 0

    # インデックスが範囲外なら最初に戻る
    if index >= len(INTERN_TOPICS):
        index = 0

    topic = INTERN_TOPICS[index]

    # カウンターを更新
    with open(COUNTER_FILE, "w", encoding="utf-8") as f:
        json.dump({"index": index + 1, "last_posted": topic["title"]}, f, ensure_ascii=False, indent=2)

    return topic["title"], topic["angle"], topic["level"], "intern"


def generate_article(topic_title=None, topic_angle=None, topic_level=None, category=None):
    """記事を生成して (title, body, topic, category) を返す"""

    if topic_title is None:
        topic_title, topic_angle, topic_level, category = get_next_topic()
    elif category is None:
        category = "intern"
        topic_level = topic_level or ""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""あなたは以下のプロフィールのnoteライターです。

【ライタープロフィール】
・22歳・理系大学4年生
・4工大（偏差値が高くない理系大学）出身
・大手金融、最大手メーカ、IT企業に内定済み（去年のサマーインターンを経て）
・就活界隈では「勝ち組」と言われる金融業界に、学歴ハンデを乗り越えて内定
・インターンや選考で出会う学生は旧帝大・早慶・MARCHばかりだった（日東駒専や大東亜帝国レベルはほぼいなかった）
・文体：ですます調の敬語。親しみやすく読みやすい文章
・一人称：僕

【シリーズコンセプト】
このnoteは「就活RPG」シリーズです。
読者が記事1から順番に読み進めることで、就活の完全初心者から内定レベルまで段階的に成長できる構成になっています。
今回の記事は「{topic_level}」のフェーズです。

【今回の記事テーマ】
タイトル：{topic_title}
記事の軸：{topic_angle}

【記事の構成】
・文字数：1000〜1300字
・冒頭：読者が「わかる！」と思える共感フレーズから入る（自慢っぽくしない）
・本文：1テーマに絞って深く書く。箇条書きよりも語りかける文体を優先
・締め：「早く動いた人が得をする」という行動を促すメッセージで終わる
・フォロー促しの一言を最後に入れる

【注意点】
・文体は必ずですます調の敬語で統一する（「だよ」「だね」などのタメ口表現は絶対に使わない）
・難しい就活用語には簡単な説明を添える
・周囲の就活生は旧帝大・早慶・MARCHが多く、4工大の自分は明らかに少数派だったというリアルを自然に盛り込む
・学歴を言い訳にしない、前向きなトーン
・自慢っぽくならず、等身大のリアルさを大事に
・実体験ベースで書く（盛りすぎない）
・マークダウン形式で出力する
・本文のみ出力（タイトルは出力しない）"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )

    body = message.content[0].text.strip()

    # ハッシュタグを末尾に追加
    hashtags = "\n\n#就活 #インターン #サマーインターン #大学生 #理系就活 #就職活動 #28卒"
    body = body + hashtags

    return topic_title, body, topic_title, category


if __name__ == "__main__":
    print("=== 就活RPG 記事テスト生成 ===")
    title, body, topic, cat = generate_article()
    print(f"タイトル: {title}")
    print(f"文字数: {len(body)}字")
    print(f"\n本文（先頭300字）:\n{body[:300]}...")
