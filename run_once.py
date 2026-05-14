"""
タスクスケジューラから呼ばれる1回投稿スクリプト
10:00 / 16:00 にそれぞれ実行される
"""
import logging
import datetime
from article_generator import generate_article
from note_poster import post_to_note
from config import PUBLISH_IMMEDIATELY

logging.basicConfig(
    filename='note_bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    encoding='utf-8'
)

def main():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] 投稿処理を開始します...")
    logging.info("投稿処理開始")

    try:
        print("記事を生成中...")
        title, body, topic, category = generate_article()
        print(f"生成完了: [{category}] {title}")
        logging.info(f"記事生成完了: {title} (トピック: {topic}, カテゴリ: {category})")

        print("note.com に投稿中...")
        success = post_to_note(title, body, publish=PUBLISH_IMMEDIATELY)

        if success:
            print("投稿成功！")
            logging.info(f"投稿成功: {title}")
        else:
            print("投稿失敗。note_bot.log を確認してください。")
            logging.error(f"投稿失敗: {title}")

    except Exception as e:
        print(f"エラー: {e}")
        logging.error(f"エラー: {e}")

if __name__ == "__main__":
    main()
