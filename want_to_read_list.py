import argparse
import pygsheets
import re
from goodreads import client
from goodreads.book import GoodreadsBook

def get_series_name_and_pos(book):
    series_title = None
    series_pos = None
    series_extended = None
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
        return None, None, None
    series_work = book.series_works.get("series_work", {})
    if not series_work:
        return None, None, None
    # If it's a list, just take the first one and so be it.
    if isinstance(series_work, list):
        series_work = series_work[0]
    # Process what you have as a dict
    series_title = series_work.get("series", {}).get("title", None)
    pos = series_work.get("user_position", "?")
    # Primary count e.g. the trilogy, vs extended count e.g. all books in same universe.
    # Ex: https://www.goodreads.com/series/135117
    # 17 primary works • 29 total works
    primary_count = series_work.get("series", {}).get("primary_work_count", "?")
    extended_count = series_work.get("series", {}).get("series_works_count", "?")
    if primary_count == extended_count:
        series_pos = "{pos} of {count}".format(pos=pos, count=primary_count)
        series_extended = None
    else:
        series_pos = "{pos} of {count}".format(pos=pos, count=primary_count)
        series_extended = extended_count
    return series_title, series_pos, series_extended

def has_genre(shelves, *targets):
    for target in targets:
        if any([x for x in shelves if target == x]):
            return "x"
    return None

NONALPHANUMERIC_PATTERN = re.compile('[\W_]+')

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
    elif show_title.lower().startswith(original_title.lower()):
        return original_title, None
    elif NONALPHANUMERIC_PATTERN.sub('', show_title).lower() == NONALPHANUMERIC_PATTERN.sub('', original_title).lower():
        return show_title, None
    else:
        return show_title, original_title

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
        "GID",
        "Phys.",
        "Kindle",
        "Author(s)",
        "Title",
        "Original Title",
        "Published",
        "Series",
        "Series #",
        "Extended",
        "Rating Dist",
        "Avg Rating",
        "# Ratings",
        "Fantasy",
        "Sci-fi",
        "Post-apoc",
        "Horror",
        "Comics",
        "Career",
        "Science",
        "Popular Shelves",
    ]
    itercount = 1
    values = []
    for review in reviews:
        try:
            book = review.book
            # Indicate progress...
            print("[%s/%s] %s ~ %s" % (itercount, len(reviews), book.gid, book.title))
            # Fetch full version of the book here, to populate things like popular shelves.
            book = gc.book(book_id=book.gid)
            # Titles
            show_title, original_title = get_titles(book)
            # Series info
            series_title, series_pos, series_extended = get_series_name_and_pos(book)
            # Genre flags?
            owned_physical = owned_kindle = ""
            if "owned-physical" in review.shelves:
                owned_physical = "x"
            if "owned-kindle" in review.shelves:
                owned_kindle = "x"
            if review.owned and int(review.owned):
                # default value is '0' (string)
                owned_physical = "?"
                owned_kindle = "?"
            fantasy = has_genre(book.popular_shelves, "fantasy")
            scifi = has_genre(book.popular_shelves, "sci-fi", "science-fiction")
            postapoc = has_genre(book.popular_shelves, "post-apocalyptic")
            horror = has_genre(book.popular_shelves, "horror")
            comics = has_genre(book.popular_shelves, "comics", "graphic-novels")
            career = has_genre(book.popular_shelves, "management", "leadership", "business")
            science = has_genre(book.popular_shelves, "academic", "research", "education")
            # Add to values array for spreadsheet.
            values.append([
                book.gid,
                owned_physical,
                owned_kindle,
                ellipsis(', '.join([author.name for author in book.authors])),
                show_title,
                original_title,
                book.publication_date[2] if book.publication_date and len(book.publication_date)==3 else None,
                series_title,
                series_pos,
                series_extended,
                book.rating_dist,
                book.average_rating,
                book.ratings_count,
                fantasy,
                scifi,
                postapoc,
                horror,
                comics,
                career,
                science,
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
