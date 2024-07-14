.PHONY: dev
dev:
	bundle exec jekyll serve

.PHONY: books
books:
	./filter_books.sh
