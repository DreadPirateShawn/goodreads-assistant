import argparse
from goodreads import client

def print_reviews(reviews):
    itercount = 1
    for review in reviews:
         book = review.book
         print("[%s/%s] %s ~ %s" % (itercount, len(reviews), book.gid, book.title))
         itercount += 1

def main(args):
    # Goodreads
    gc = client.GoodreadsClient(args.goodreads_key, args.goodreads_secret)

    reviews = gc.shelf(args.goodreads_user, 'read', show_progress=True)
    print("== Reviews: %s ==" % len(reviews))

    reviews = [review for review in reviews if not review.rating]
    print("== Reviews: %s ==" % len(reviews))

    print_reviews(reviews)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--goodreads-key', type=str, help='Goodreads API key', required=True)
    parser.add_argument('--goodreads-secret', type=str, help='Goodreads API secret', required=True)
    parser.add_argument('--goodreads-user', type=str, help='Goodreads user', required=True)
    args = parser.parse_args()
    main(args)
