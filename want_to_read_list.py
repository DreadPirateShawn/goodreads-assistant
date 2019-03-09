import argparse
import pygsheets
from goodreads import client
from goodreads.book import GoodreadsBook

def get_series_name_and_pos(book):
    series_title = None
    series_pos = None
    #   OrderedDict([
    #    ('series_work', OrderedDict([
    #      ('id', '841082'),
    #      ('user_position', '1'),
    #      ('series', OrderedDict([
    #        ('id', '166200'),
    #        ('title', 'Terra Ignota'),
    #        ('description', 'Science fiction often has...'),
    #        ('note', None),
    #        ('series_works_count', '4'),
    #        ('primary_work_count', '4'),
    #        ('numbered', 'true')]))]))])

    # Check for absent, or for multiple series (e.g. Swamp Thing comics)
    if not book.series_works:
        return None, None
    series_work = book.series_works.get("series_work", {})
    if not series_work:
        return None, None
    if isinstance(series_work, list):
        return "(multiple series)", None

    # Otherwise process as a dict
    series_title = series_work.get("series", {}).get("title", None)
    series_pos = "{pos} of {count} or {count2}".format(
        pos = series_work.get("user_position", "?"),
        count = series_work.get("series", {}).get("series_works_count", "?"),
        count2 = series_work.get("series", {}).get("primary_work_count", "?"))
    return series_title, series_pos

def has_genre(shelves, *targets):
    for target in targets:
        if any([x for x in shelves if target in x]):
            return "x"
    return None

def get_titles(book):
    show_title = book.title
    original_title = book.work.get("original_title", None)
    # If the display title starts with the original title,
    # then it probably has the series appended. Strip it here,
    # we show series elsewhere.
    if not original_title:
        return show_title, None
    if isinstance(original_title, dict):
        # Sometimes this comes back as OrderedDict([('@nil', 'true')]), e.g. gid 18923413
        return show_title, None
    elif show_title.startswith(original_title):
        return original_title, None
    else:
        return show_title, original_title

def ellipsis(raw):
    maxlen = 50
    return (raw[:maxlen-3] + '...') if len(raw) > maxlen else raw

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
        "Series #",
        "Series Works",
        "Rating Dist",
        "Avg Rating",
        "# Ratings",
        "Fantasy",
        "Sci-fi",
        "Post-apoc",
        "Horror",
        "Comics",
        "Career",
        "Series",
        "Popular Shelves",
    ]
    itercount = 1
    values = []
    for book in books:
        try:
            # Indicate progress...
            print("[%s/%s] %s ~ %s" % (itercount, len(books), book.gid, book.title))
            # Fetch full version of the book here, to populate things like popular shelves.
            book = gc.book(book_id=book.gid)
            # Titles
            show_title, original_title = get_titles(book)
            # Series info
            series_title, series_pos = get_series_name_and_pos(book)
            # Genre flags?
            fantasy = has_genre(book.popular_shelves, "fantasy")
            scifi = has_genre(book.popular_shelves, "sci-fi", "science-fiction")
            postapoc = has_genre(book.popular_shelves, "post-apocalyptic")
            horror = has_genre(book.popular_shelves, "horror")
            comics = has_genre(book.popular_shelves, "comics", "graphic-novels")
            career = has_genre(book.popular_shelves, "management", "leadership", "business")
            # Add to values array for spreadsheet.
            values.append([
                book.gid,
                ellipsis(', '.join([author.name for author in book.authors])),
                show_title,
                original_title,
                book.publication_date[2] if book.publication_date and len(book.publication_date)==3 else None,
                series_title,
                series_pos,
                book.rating_dist,
                book.average_rating,
                book.ratings_count,
                fantasy,
                scifi,
                postapoc,
                horror,
                comics,
                career,
                str(book.series_works),
                str(book.popular_shelves),
            ])
            itercount += 1
        except:
            print(book._book_dict)
            raise

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
