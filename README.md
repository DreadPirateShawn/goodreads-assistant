## Prepping a virtual env
```
pip install virtualenv
python -m virtualenv venv
source venv/bin/activate
```

Once inside the virtual env:
```
pip install -r requirements.txt
```

## Generating / updating the spreadsheet
Prerequisite:
```
cp ~/Downloads/client_secret*.json .
```
Then something along the lines of:
```
SPREADSHEET_ID=foo
GOODREADS_KEY=foo
GOODREADS_SECRET=foo
GOODREADS_USER=foo
```
Generate highly customized spreadsheet of books on "to-read" shelf.
```
python3 want_to_read_list.py \
  --spreadsheet $SPREADSHEET_ID \
  --goodreads-key $GOODREADS_KEY \
  --goodreads-secret $GOODREADS_SECRET \
  --goodreads-user $GOODREADS_USER \
  --goodreads-shelf 'to-read'
```
Print books on "read" shelf without a personal rating.
```
python3 unrated.py \
  --spreadsheet $SPREADSHEET_ID \
  --goodreads-key $GOODREADS_KEY \
  --goodreads-secret $GOODREADS_SECRET \
  --goodreads-user $GOODREADS_USER
```
Print books on "read" shelf but not in explicit star-count shelves.
```
python3 shelf_combos.py \
  --goodreads-key $GOODREADS_KEY \
  --goodreads-secret $GOODREADS_SECRET \
  --goodreads-user $GOODREADS_USER \
  --goodreads-shelf 'read' \
  --goodreads-no-shelf '1-star' \
  --goodreads-no-shelf '2-star' \
  --goodreads-no-shelf '3-star' \
  --goodreads-no-shelf '4-star' \
  --goodreads-no-shelf '5-star'
```
Print books on "sci-fi" shelf but not in any sub-genre shelf.
```
python3 shelf_combos.py \
  --goodreads-key $GOODREADS_KEY \
  --goodreads-secret $GOODREADS_SECRET \
  --goodreads-user $GOODREADS_USER \
  --goodreads-shelf 'sci-fi' \
  --goodreads-no-shelf 'sci-fi-cyberpunk' \
  --goodreads-no-shelf 'sci-fi-dying-earth' \
  --goodreads-no-shelf 'sci-fi-hard' \
  --goodreads-no-shelf 'sci-fi-space-opera' \
  --goodreads-no-shelf 'sci-fi-steampunk'
```
