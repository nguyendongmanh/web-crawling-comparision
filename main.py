import time
import argparse
from src.crawler.dantri import Dantri


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl news from Dantri.")
    parser.add_argument(
        "method",
        type=str,
        help="There are 3 methods: sequential, parallel and async.",
        choices=["sequential", "parallel", "async"],
        default="sequential",
    )
    parser.add_argument(
        "--eval",
        help="Evaluate the performance of each method.",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()

    start_time = time.time()
    if args.method == "sequential":
        dantri = Dantri()
        news = dantri.crawl(max_pagination=1)
        if args.eval:
            print(f"Total time: {time.time() - start_time}")
