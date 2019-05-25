## Prepping a virtual env
```
pip install virtualenv
python -m virtualenv venv
source venv/bin/activate
```

Once inside the virtual env:
```
pip install https://github.com/nithinmurali/pygsheets/archive/master.zip
pip install Goodreads
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

python3 want_to_read_list.py \
  --spreadsheet $SPREADSHEET_ID \
  --goodreads-key $GOODREADS_KEY \
  --goodreads-secret $GOODREADS_SECRET \
  --goodreads-user $GOODREADS_USER \
  --goodreads-shelf 'to-read'
```
