# Comparing methods in Crawling Data

## Instructions
To run programming, firstly, you need to create the virtual environment to manage python packages.
```bash
# create venv
conda create -n p-fp-env python=3.11
# activate this environment
conda activate p-fp-env
# install packages
pip install -r requirements.txt
```
After finishing installation, to understand how this project work, try
```bash
python main.py -h
```
The result of this command is:
```bash
usage: main.py [-h] [--max_pagination MAX_PAGINATION]
               [--num_workers NUM_WORKERS] [--num_links NUM_LINKS]
               {sync,thread,async}

Crawl news from Dantri.

positional arguments:
  {sync,thread,async}   There are 3 methods: `sync`, `thread` and `async`.
                        Default is `sync`

options:
  -h, --help            show this help message and exit
  --max_pagination MAX_PAGINATION
                        Number of paginations in each topic. Default is 1.
  --num_workers NUM_WORKERS
                        Number of consumer workers. Default is 4.
  --num_links NUM_LINKS
                        The number of links. Default is 1000

```
With information, you can run `main.py`, for example,
```bash
python main.py sync --num_links 1000 --max_pagination 10
```
or
```bash
python main.py thread --num_links 1000 --max_pagination 10 --num_workers 4
```

## Results
| Number of Tasks (n) | Synchronous Time (s) | Thread (4) Time (s) | Thread (8) Time (s) |
|---------------------|----------------------|---------------------|---------------------|
| 500                 | 311                  | 105                 | 58                  |
| 1000                | 614                  | 161                 | 101                 |
| 2000                | 1819                 | 388                 | 218                 |

![alt text](https://github.com/nguyendongmanh/web-crawling-comparision/blob/master/images/output.jpg?raw=true)
