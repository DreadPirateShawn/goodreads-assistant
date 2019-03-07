import argparse
import pygsheets
from goodreads import client
from goodreads.book import GoodreadsBook

def main(args):
    # Goodreads
    gc = client.GoodreadsClient(args.goodreads_key, args.goodreads_secret)
    books = gc.shelf(args.goodreads_user, args.goodreads_shelf, show_progress=True)
    books.sort(key=lambda x: x.authors[0].name)

    # Data prep
    headers = [
        "Author(s)",
        "Title",
        "Avg Rating",
        "# Ratings",
        "Popular Shelves",
        "Work",
        "Series Works",
        "Publication Date",
    ]
    values = []
    for book in books:
        values.append([
            ', '.join([author.name for author in book.authors]),
            book.title,
            book.average_rating,
            book.ratings_count,
            str(book.popular_shelves),
            str(book.work),
            str(book.series_works),
            book.publication_date[2] if book.publication_date and len(book.publication_date)==3 else None,
        ])

    # Sheets
    gc = pygsheets.authorize()
    sheet = gc.open_by_key(args.spreadsheet)
    tab_name = "Main"
    try:
        wks = sheet.worksheet_by_title(tab_name)
    except pygsheets.exceptions.WorksheetNotFound:
        wks = sheet.add_worksheet(tab_name)
    wks.clear()
    wks.resize(rows=len(values) + 1, cols=len(headers))
    wks.update_values(crange='A1', values=[headers])
    wks.update_values(crange='A2', values=values)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--spreadsheet', type=str, help='Spreadsheet ID', required=True)
    parser.add_argument('--goodreads-key', type=str, help='Goodreads API key', required=True)
    parser.add_argument('--goodreads-secret', type=str, help='Goodreads API secret', required=True)
    parser.add_argument('--goodreads-user', type=str, help='Goodreads user', required=True)
    parser.add_argument('--goodreads-shelf', type=str, help='Goodreads shelf', required=True)
    args = parser.parse_args()
    main(args)
