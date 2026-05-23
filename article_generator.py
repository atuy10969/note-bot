import anthropic
import datetime
import json
import os
from config import ANTHROPIC_API_KEY

COUNTER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "article_counter.json")

# 就活RPGシリーズ — 記事1から順番に読み進めることで初心者→内定レベルに成長できる構成
RPG_SERIES = [
    # ── CHAPTER 1: 就活を始める前の心構え ──
    {
        "no": 1,
        "title": "【就活RPG①】就活って何から始めればいい？初心者がまず知るべきこと",
        "angle": "就活の全体像を初心者向けにざっくり解説。何も知らない状態から動き始めるための第一歩"
    },
    {
        "no": 2,
        "title": "【就活RPG②】学歴コンプを抱えたまま就活を始めた話",
        "angle": "4工大出身として感じていた不安と、それでも動き出せた理由。読者の共感を引き出す"
    },
    {
        "no": 3,
        "title": "【就活RPG③】就活のスケジュール、いつ何をすればいい？逆算で考える",
        "angle": "サマーインターンから本選考までの時系列を整理。いつ動けばいいかの全体像"
    },
    # ── CHAPTER 2: 自己分析 ──
    {
        "no": 4,
        "title": "【就活RPG④】自己分析って何のためにするの？意味を理解してから始める",
        "angle": "自己分析の目的を腹落ちさせる。やらされ感をなくすための考え方"
    },
    {
        "no": 5,
        "title": "【就活RPG⑤】自己分析のやり方、具体的に何をすればいい？",
        "angle": "実際にやった自己分析の方法を手順で解説。モットー・強み・エピソードの掘り起こし方"
    },
    {
        "no": 6,
        "title": "【就活RPG⑥】ガクチカが書けない人へ。研究・バイト・サークルをESに変換する方法",
        "angle": "「特別なことをしていない」人のガクチカの作り方。エピソードの掘り下げ方"
    },
    # ── CHAPTER 3: 業界・企業研究 ──
    {
        "no": 7,
        "title": "【就活RPG⑦】業界研究って何のためにするの？就活初心者が陥るミス",
        "angle": "業界研究の目的と、やらないと選考で詰まる理由。情報収集の考え方"
    },
    {
        "no": 8,
        "title": "【就活RPG⑧】理系が金融業界を受けていい理由、全部話す",
        "angle": "理系×金融という組み合わせへの疑問を払拭。実体験から語る"
    },
    {
        "no": 9,
        "title": "【就活RPG⑨】インターン選び「大手だけ」に絞ると詰む理由",
        "angle": "大手一本絞りのリスクと、中小・ベンチャーインターンの価値"
    },
    # ── CHAPTER 4: 逆求人・ツール活用 ──
    {
        "no": 10,
        "title": "【就活RPG⑩】逆求人サービスに登録してない就活生、正直もったいなすぎる",
        "angle": "逆求人の仕組みと使わないと損する理由を実体験で語る"
    },
    {
        "no": 11,
        "title": "【就活RPG⑪】OfferBoxとキミスカ、実際に両方使って感じた違い",
        "angle": "2つの逆求人サービスの比較。どんな人にどっちが向いてるか"
    },
    {
        "no": 12,
        "title": "【就活RPG⑫】スカウトが全然来ない人がやりがちなプロフィールのミス",
        "angle": "逆求人でスカウトが来ない原因と、すぐ直せる改善ポイント"
    },
    # ── CHAPTER 5: ES・書類対策 ──
    {
        "no": 13,
        "title": "【就活RPG⑬】ESの書き出しで落とされてる可能性がある話",
        "angle": "ESの冒頭一文で印象が決まる理由と、刺さる書き出しの作り方"
    },
    {
        "no": 14,
        "title": "【就活RPG⑭】自己分析を「言語化」できてないESは全部同じに見える",
        "angle": "自己分析をESに落とし込む方法。なぜ言語化が大事か"
    },
    {
        "no": 15,
        "title": "【就活RPG⑮】学歴フィルターを実際に食らった話と、その回避法",
        "angle": "エントリー画面で弾かれた経験と、そこから取った戦略"
    },
    # ── CHAPTER 6: OB訪問 ──
    {
        "no": 16,
        "title": "【就活RPG⑯】OB訪問を1回やるだけで変わること、実体験で語る",
        "angle": "OB訪問前後で就活の解像度がどう変わったか。具体的な変化"
    },
    {
        "no": 17,
        "title": "【就活RPG⑰】Matcherでのアポの取り方、メッセージ文そのまま公開",
        "angle": "OB訪問のアポメッセージのテンプレ。断られにくい書き方"
    },
    {
        "no": 18,
        "title": "【就活RPG⑱】OB訪問で絶対に聞くべき質問リスト、ネットには載ってないやつ",
        "angle": "表面的でない、本音を引き出す質問の仕方"
    },
    # ── CHAPTER 7: インターン選考対策 ──
    {
        "no": 19,
        "title": "【就活RPG⑲】インターン面接で落ちる人に共通する話し方のクセ",
        "angle": "面接でやりがちなNG行動と、意識するだけで変わる話し方"
    },
    {
        "no": 20,
        "title": "【就活RPG⑳】グループワークで埋もれない立ち回り方、金融インターンで学んだこと",
        "angle": "GD・グループワークでの立ち位置の取り方。整理役・調整役という戦略"
    },
    {
        "no": 21,
        "title": "【就活RPG㉑】インターン当日、緊張しすぎて失敗した話と反省",
        "angle": "本番で起きたリアルな失敗談と、そこから学んだこと"
    },
    # ── CHAPTER 8: 本選考・内定 ──
    {
        "no": 22,
        "title": "【就活RPG㉒】サマーインターンが終わった後、何をすればいい？",
        "angle": "インターン後の動き方。早期選考・本選考への繋げ方"
    },
    {
        "no": 23,
        "title": "【就活RPG㉓】4工大から大手金融に内定した話、全部話す",
        "angle": "選考フロー・対策・当日の空気感まで、リアルな体験談"
    },
    {
        "no": 24,
        "title": "【就活RPG㉔】就活を終えて思うこと。学歴より大事だったもの",
        "angle": "就活全体を振り返って気づいたこと。後輩へのメッセージ"
    },
]


def _load_counter() -> int:
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("next_index", 0)
    return 0


def _save_counter(index: int):
    with open(COUNTER_FILE, "w", encoding="utf-8") as f:
        json.dump({"next_index": index, "total": len(RPG_SERIES)}, f, ensure_ascii=False, indent=2)


def get_next_article() -> dict:
    """次に投稿すべき記事を返す（カウンターを1つ進める）"""
    idx = _load_counter()
    article = RPG_SERIES[idx % len(RPG_SERIES)]
    _save_counter((idx + 1) % len(RPG_SERIES))
    return article


def generate_article(article: dict | None = None) -> tuple[str, str, str, str]:
    """記事を生成して (title, body, topic, category) を返す"""

    if article is None:
        article = get_next_article()

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
このnoteは「就活RPG」シリーズです。読者が記事1から順番に読み進めることで、就活の完全初心者から内定レベルまで段階的に成長できる構成になっています。

【今回の記事】
記事番号：{article['no']}
タイトル：{article['title']}
記事の軸：{article['angle']}

【記事の構成】
・文字数：1000〜1300字
・冒頭：読者が「わかる！」と思える共感フレーズから入る（自慢っぽくしない）
・本文：1テーマに絞って深く書く。箇条書きよりも語りかける文体を優先
・締め：「早く動いた人が得をする」という行動を促すメッセージで終わる
・フォロー促しの一言を最後に入れる

【タイトルについて】
タイトルはそのまま使うので変更しないでください：
{article['title']}

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

    hashtags = "\n\n#就活 #インターン #サマーインターン #大学生 #理系就活 #就職活動 #28卒"
    body = body + hashtags

    return article["title"], body, article["title"], "intern"


if __name__ == "__main__":
    print("=== 就活RPGシリーズ 記事テスト生成 ===")
    idx = _load_counter()
    next_article = RPG_SERIES[idx % len(RPG_SERIES)]
    print(f"次の記事: No.{next_article['no']} / 全{len(RPG_SERIES)}記事")
    print(f"タイトル: {next_article['title']}")
    print()
    title, body, topic, cat = generate_article()
    print(f"タイトル: {title}")
    print(f"\n本文（先頭200字）:\n{body[:200]}...")
    print(f"\n総文字数: {len(body)}字")
