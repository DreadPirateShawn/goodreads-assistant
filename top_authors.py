import argparse
import pygsheets
from collections import OrderedDict
from statistics import mean
from goodreads import client
from goodreads.book import GoodreadsBook

def ellipsis(raw):
    maxlen = 50
    return (raw[:maxlen-3] + '...') if len(raw) > maxlen else raw

def main(args):
    # Goodreads
    gc = client.GoodreadsClient(args.goodreads_key, args.goodreads_secret)
    reviews = gc.shelf(args.goodreads_user, args.goodreads_shelf, show_progress=True)
    reviews.sort(key=lambda x: x.book.authors[0].name)

    # Data prep
    headers = [
        "Author(s)",
        "Max",
        "Avg",
        "#",
    ]
    itercount = 1
    authors = {}
    for review in reviews:
        try:
            book = review.book
            print("[%s/%s] %s ~ %s" % (itercount, len(reviews), book.gid, book.title))
            if len(book.authors) > 1:
                print(" - multiple authors: %s" % ', '.join([author.name for author in book.authors]))
            primary_author = book.authors[0].name
            authors[primary_author] = authors.get(primary_author, []) + [int(review.rating)]
            itercount += 1
        except:
            print(book._book_dict)
            raise
    values = []
    # Sort authors data by: max rating, avg rating
    authors = OrderedDict(sorted(authors.items(),
                                 key=lambda ratings: (max(ratings[1]), mean(ratings[1]), len(ratings[1])),
                                 reverse=True))
    for author, ratings in authors.items():
        # Add to values array for spreadsheet.
        values.append([
            author,
            max(ratings),
            "{:.1f}".format(mean(ratings)),
            len(ratings),
        ])

    # Sheets
    gc = pygsheets.authorize()
    sheet = gc.open_by_key(args.spreadsheet)
    tab_name = "Top Authors"
    try:
        wks = sheet.worksheet_by_title(tab_name)
    except pygsheets.exceptions.WorksheetNotFound:
        wks = sheet.add_worksheet(tab_name)
    wks.clear()
    wks.resize(rows=len(values) + 1, cols=len(headers))
    try:
        wks.update_values(crange='A1', values=[headers])
        wks.update_values(crange='A2', values=values)
    except:
        print(values)
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--spreadsheet', type=str, help='Spreadsheet ID', required=True)
    parser.add_argument('--goodreads-key', type=str, help='Goodreads API key', required=True)
    parser.add_argument('--goodreads-secret', type=str, help='Goodreads API secret', required=True)
    parser.add_argument('--goodreads-user', type=str, help='Goodreads user', required=True)
    parser.add_argument('--goodreads-shelf', type=str, help='Goodreads shelf', required=True)
    args = parser.parse_args()
    main(args)
