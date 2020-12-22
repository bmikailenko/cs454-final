Ben Mikailenko
Trey Fontaine

MetaCritic Searcher

Files:
	best_games_user.py - scrapes metacritic and creates data/best-User-games.csv
	build_index.py - builds a Whoosh! index over best-User-games.csv
	metacritic_searcher.py - runs the MetaCritic Searcher server on http://127.0.0.1:5000/

To run:
	- build the index. Takes 10 minutes. 
	python3 build_index.py

	- run the website
	python3 metacritic_searcher.py
	


