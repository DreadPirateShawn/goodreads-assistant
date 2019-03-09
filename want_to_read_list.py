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
        "GID",
        "Author(s)",
        "Title",
        "Original Title",
        "Published",
        "Rating Dist",
        "Avg Rating",
        "# Ratings",
        "Fantasy",
        "Sci-fi",
        "Post-apocalyptic",
        "Horror",
        "Series",
        "Series #",
        "Series Works",
        "Popular Shelves",
    ]
    itercount = 1
    values = []
    for book in books:
        # Indicate progress...
        print("[%s/%s] %s" % (itercount, len(books), book.title))
        # Fetch full version of the book here, to populate things like popular shelves.
        book = gc.book(book_id=book.gid)
        # Original title
        original_title = book.work.get("original_title", None) #if book.work else None
        # Series info
        if book.series_works:
            # OrderedDict([
            #  ('series_work', OrderedDict([
            #    ('id', '841082'),
            #    ('user_position', '1'),
            #    ('series', OrderedDict([
            #      ('id', '166200'),
            #      ('title', 'Terra Ignota'),
            #      ('description', 'Science fiction often has...'),
            #      ('note', None),
            #      ('series_works_count', '4'),
            #      ('primary_work_count', '4'),
            #      ('numbered', 'true')]))]))])
            series_title = book.series_works.get("series_work", {}).get("series", {}).get("title", None)
            series_pos = "{pos} of {count} or {count2}".format(
                pos = book.series_works.get("series_work", {}).get("user_position", "?"),
                count = book.series_works.get("series_work", {}).get("series", {}).get("series_works_count", "?"),
                count2 = book.series_works.get("series_work", {}).get("series", {}).get("primary_work_count", "?"))
        else:
            series_title = series_pos = None
        # Genre flags?
        fantasy = "x" if any([x for x in book.popular_shelves if "fantasy" in x]) else ""
        scifi = "x" if any([x for x in book.popular_shelves if "sci-fi" in x or "science-fiction" in x]) else ""
        postapoc = "x" if any([x for x in book.popular_shelves if "post-apocalyptic" in x]) else ""
        horror = "x" if any([x for x in book.popular_shelves if "horror" in x]) else ""
        # Add to values array for spreadsheet.
        values.append([
            book.gid,
            ', '.join([author.name for author in book.authors]),
            book.title,
            original_title,
            book.publication_date[2] if book.publication_date and len(book.publication_date)==3 else None,
            book.rating_dist,
            book.average_rating,
            book.ratings_count,
            fantasy,
            scifi,
            postapoc,
            horror,
            series_title,
            series_pos,
            str(book.series_works),
            str(book.popular_shelves),
        ])
        itercount += 1

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
