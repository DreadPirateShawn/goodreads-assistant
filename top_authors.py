import argparse
import pygsheets
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
        "Title",
        "My Rating",
    ]
    itercount = 1
    values = []
    for review in reviews:
        try:
            book = review.book
            # Indicate progress...
            print("[%s/%s] %s ~ %s" % (itercount, len(reviews), book.gid, book.title))

            # Add to values array for spreadsheet.
            values.append([
                ellipsis(', '.join([author.name for author in book.authors])),
                book.title,
                review.rating,
            ])
            itercount += 1
        except:
            print(book._book_dict)
            raise

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
