# yc-collision

type in a one-sentence startup idea and get back the Y Combinator companies
whose descriptions are closest in meaning, including ones that shut down or
got acquired. i built it for checking what's already been tried before you build.

it uses semantic search, so it matches on meaning, not keywords. searching for
"send big files between people privately" finds a company described as "really
secure file sending for big files" even though almost none of the words match.

## Example

```
$ python scripts/search.py "secure peer-to-peer service for sending large files"

 1. WireOver  [0.662]
    Winter 2012 | Inactive | B2B
    Really secure file sending for big files.
    https://www.ycombinator.com/companies/wireover

 2. Sendoid  [0.614]
    Winter 2011 | Acquired | B2B
    High speed peer to peer data transport technology for consumers
    https://www.ycombinator.com/companies/sendoid
```

The number in brackets is a similarity score. Higher means closer in meaning.

## Setup

You need Python 3.11 or newer.

```
git clone https://github.com/batyrkhan9/yc-collision.git
cd yc-collision

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Build the data

The company data and the search index aren't stored in the repo, so build them
once. Run these in order:

```
python scripts/download_data.py     # download the YC company list
python scripts/clean_data.py        # keep the fields we need
python scripts/build_embeddings.py  # turn each company into a vector
```

`build_embeddings.py` downloads a small model (~90 MB) the first time and takes
a minute or two to run.

## Search

```
python scripts/search.py "an app that delivers groceries in under an hour"
python scripts/search.py "peer-to-peer file sharing" --top 15
```

Use `--top` to change how many results you get (default is 10).

## How it works

1. Download ~6,000 YC companies from the public
   [yc-oss API](https://yc-oss.github.io/api/).
2. Keep a few useful fields per company: name, description, industry, tags,
   batch, status, and URL.
3. Turn each company's text into a list of numbers (an "embedding") that
   captures its meaning, using a local
   [sentence-transformers](https://www.sbert.net/) model. Nothing is sent to an
   API, and it runs offline after the first download.
4. When you search, turn your sentence into a vector the same way and find the
   companies whose vectors point in the most similar direction.

## What's in here

```
scripts/download_data.py     download the raw company list
scripts/validate_data.py     print counts and sample records to sanity-check the data
scripts/clean_data.py        flatten the raw data into the fields we use
scripts/build_embeddings.py  build the search index
scripts/search.py            run a search
```
