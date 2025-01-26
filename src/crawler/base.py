from typing import Dict, Any
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class TYPE(Enum):
    NORMAL = 1


@dataclass
class News:
    title: str
    author: str
    created_at: datetime
    content: str
    type: TYPE
    category: str
    url: str


class BaseCrawler(ABC):

    def __init__(self, *args, **kwargs):
        self.__timeout = kwargs.get("timeout", 60)
        self.__parent_url = kwargs.get("parent_url", None)
        self.__n_news = kwargs.get("n_news", 100)

        assert self.__parent_url is not None, "parent_url must be provided."

    @classmethod
    def from_dict(cls, config: Dict[str, Any]):
        return cls(config)

    @property
    def timeout(self):
        return self.__timeout

    @property
    def parent_url(self):
        return self.__parent_url

    @property
    def number_of_news(self):
        return self.__n_news

    @abstractmethod
    def _scrape_news(self, url: str) -> News:
        raise NotImplementedError("_scrape_news() must be implemented.")

    @abstractmethod
    def crawl(self):
        raise NotImplementedError("crawl() must be implemented.")
