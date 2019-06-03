import argparse
from goodreads import client

def print_reviews(reviews):
    itercount = 1
    for review in reviews:
        try:
            book = review.book
            print("[%s/%s] %s ~ %s" % (itercount, len(reviews), book.gid, book.title))
            itercount += 1
        except:
            print(review._review_dict)
            raise

def main(args):
    # Goodreads
    gc = client.GoodreadsClient(args.goodreads_key, args.goodreads_secret)

    reviews = set()
    print("== Reviews: %s ==" % len(reviews))

    for shelf in args.goodreads_shelf:
        print("+Shelf: %s" % shelf)
        results = gc.shelf(args.goodreads_user, shelf, show_progress=True)
        print_reviews(results)
        gids = [review.book.gid for review in results]
        reviews = results + [review for review in reviews if review.book.gid not in gids]
        print("== Reviews: %s ==" % len(reviews))

    for shelf in args.goodreads_no_shelf:
        print("-Shelf: %s" % shelf)
        results = gc.shelf(args.goodreads_user, shelf, show_progress=True)
        print_reviews(results)
        gids = [review.book.gid for review in results]
        reviews = [review for review in reviews if review.book.gid not in gids]
        print("== Reviews: %s ==" % len(reviews))

    print("== FINAL ==")
    print_reviews(reviews)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--goodreads-key', type=str, help='Goodreads API key', required=True)
    parser.add_argument('--goodreads-secret', type=str, help='Goodreads API secret', required=True)
    parser.add_argument('--goodreads-user', type=str, help='Goodreads user', required=True)
    parser.add_argument('--goodreads-shelf', type=str, action='append', help='Goodreads shelves to include', required=True)
    parser.add_argument('--goodreads-no-shelf', type=str, action='append', help='Goodreads shelves to exclude', required=True)
    args = parser.parse_args()
    main(args)
