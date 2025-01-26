import requests
from bs4 import BeautifulSoup
from functools import wraps
from typing import Callable


def retry(times: int):
    def decorator(func: Callable):
        @wraps(func)
        def warpper(url: str, *args, **kwargs):
            attempt = 0
            while attempt <= times:
                try:
                    return func(url, *args, **kwargs)
                except Exception:
                    print(
                        "Error loadding page, load again!. There are {} times left".format(
                            times - attempt
                        )
                    )
                attempt += 1
            return None

        return warpper

    return decorator


def get_soup(func: Callable):
    @wraps(func)
    def wrapper(url: str, *args, **kwargs):
        content = func(url, *args, **kwargs)
        assert content is not None, "Cannot load page"
        soup = BeautifulSoup(content, "lxml")

        return soup

    return wrapper


@get_soup
@retry(times=3)
def fetch(url: str, *args, **kwargs) -> str:
    timeout = kwargs.get("timeout", 60)
    response = requests.get(url, timeout=timeout)

    assert response.status_code == 200, "Cannot load page"

    return response.text


if __name__ == "__main__":
    fetch(url="https://dantri.com.vn/", timeout=10)
