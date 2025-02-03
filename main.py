import os
import json
import time
import argparse
from queue import Queue
from tqdm import tqdm

from src.crawler.dantri import Dantri
from worker import Producer, Consumer

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl news from Dantri.")
    parser.add_argument(
        "method",
        type=str,
        help="There are 3 methods: `sync`, `thread` and `async`. Default is `sync`",
        choices=["sync", "thread", "async"],
        default="sync",
    )

    parser.add_argument(
        "--max_pagination",
        type=int,
        help="Number of paginations in each topic. Default is 1.",
        default=1,
    )

    parser.add_argument(
        "--num_workers",
        type=int,
        help="Number of consumer workers. Default is 4.",
        default=4,
    )

    parser.add_argument(
        "--num_links",
        type=int,
        help="The number of links. Default is 1000",
        default=1000,
    )

    args = parser.parse_args()

    q = Queue()
    dantri = Dantri()

    if os.path.exists("data/urls.json"):
        with open("data/urls.json", "r", encoding="utf-8") as f:
            links = json.load(f)
            links = links[: args.num_links]
    else:
        assert (
            args.max_pagination > 0
        ), "The number of paginations must be greater than 0"

        print(
            f"Start the crawling process, for each topic you will go through a maximum of {args.max_pagination} pages."
        )

        links = dantri.crawl(max_pagination=args.max_pagination, link_only=True)
        with open("data/urls.json", "w", encoding="utf-8") as f:
            json.dump(links, f, ensure_ascii=False, indent=4)

    start_time = time.time()
    if args.method == "sync":
        print("-------------------- Synchronous --------------------")
        scrape_news = dantri.scrape_news()

        for link in tqdm(links):
            result = scrape_news(url=link)
            time.sleep(0.5)

        print(f"Sync took {time.time() - start_time} to finish")
    elif args.method == "thread":
        print("-------------------- Threading --------------------")
        assert args.num_workers > 0, "The number of workers must be greater than 0"
        progress_bar = tqdm(total=len(links), desc="Crawling URLs", unit="URL")

        producer = Producer(q, links)

        producer.start()

        consumers = []

        for id in range(args.num_workers):
            consumer = Consumer(
                queue=q,
                instance=dantri,
                sleep_time=0.5,
                consumer_id=id,
                progress_bar=progress_bar,
            )
            consumer.start()
            consumers.append(consumer)

        producer.join()
        q.join()

        [consumer.join() for consumer in consumers]
        progress_bar.close()
        print(f"Thread took {time.time() - start_time} to finish")

    elif args.method == "async":
        print("-------------------- Asynchronous --------------------")
        pass
