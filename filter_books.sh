grep \
  -e'^$' \
  -e'- Title:' \
  -e'  Author:' \
  -e'  Pages:' \
  -e'  Rating:' \
  -e'  Read:' \
  -e'  Reread:' \
  -e'  Audiobook:' \
  ../Notes/personal/books.md \
  > _data/books.yml
