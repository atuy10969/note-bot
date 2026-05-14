import datetime
import time
import schedule
import logging
from article_generator import generate_article
from note_poster import post_to_note
from config import POST_TIMES, PUBLISH_IMMEDIATELY

logging.basicConfig(
    filename='note_bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    encoding='utf-8'
)

def job():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{now}] 投稿処理を開始します...")
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
            print("投稿失敗。ログを確認してください。")
            logging.error(f"投稿失敗: {title}")

    except Exception as e:
        print(f"エラー: {e}")
        logging.error(f"エラー: {e}")

def main():
    print(f"note自動投稿ボットを起動しました")
    print(f"毎日 {', '.join(POST_TIMES)} に投稿します")
    print("停止するには Ctrl+C を押してください\n")

    for post_time in POST_TIMES:
        schedule.every().day.at(post_time).do(job)
        print(f"スケジュール登録: {post_time}")

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
