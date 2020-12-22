from flask import Flask, render_template, url_for, request
import whoosh
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh import qparser
import math

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])

def index():
	print('Rendered welcome page')
	return render_template('welcome_page.html')

@app.route('/results/', methods=['GET', 'POST'])

@app.route('/reviews/', methods=['GET', 'POST'])

def results():
	global mysearch
	if request.method == 'POST':
		data = request.form
		print("form")
		print(data)
		print("end of data")
	else:
		data = request.args
		print("args")
		print(data)

	review_request = data.get('review_request')

	# requesting the reviews.html page
	if (review_request != None):

		keywordquery = data.get('searchterm').replace("/","")
		page = data.get('page').replace("/","")
		platforms = data.get('platforms').replace("/","")
		genres = data.get('genres').replace("/","")
		years_from = data.get('years_from').replace("/","")
		years_to = data.get('years_to').replace("/","")
		metacritic_score_from = data.get('metacritic_score_from').replace("/","")
		metacritic_score_to = data.get('metacritic_score_to').replace("/","")
		user_score_from = data.get('user_score_from').replace("/","")
		user_score_to = data.get('user_score_to').replace("/","")
		user_input = [keywordquery, platforms, genres, years_from, years_to, metacritic_score_from, metacritic_score_to, user_score_from, user_score_to, page]


		review_request = review_request.replace("/","")
		user = data.get('user')
		names, dates, user_rev_scores, reviews, game_title, titles = mysearch.review_search(review_request, user)
		return render_template('reviews.html', results=zip(names, dates, user_rev_scores, reviews, titles), game_title=game_title, user_input=user_input)
	
	# requesting the results.html page
	else:
		keywordquery = data.get('searchterm').replace("/","")
		page = data.get('page').replace("/","")
		platforms = data.get('platforms').replace("/","")
		genres = data.get('genres').replace("/","")
		years_from = data.get('years_from').replace("/","")
		years_to = data.get('years_to').replace("/","")
		metacritic_score_from = data.get('metacritic_score_from').replace("/","")
		metacritic_score_to = data.get('metacritic_score_to').replace("/","")
		user_score_from = data.get('user_score_from').replace("/","")
		user_score_to = data.get('user_score_to').replace("/","")
		user_input = [keywordquery, platforms, genres, years_from, years_to, metacritic_score_from, metacritic_score_to, user_score_from, user_score_to, page]
		titles, platforms, urls, user_scores, summaries, dates, meta_scores, images, genres, page, total_pages, total_results, reviews = mysearch.search(keywordquery, platforms, genres, user_score_from, user_score_to, metacritic_score_from, metacritic_score_to, page, years_from, years_to)
		return render_template('results.html', query=keywordquery, results=zip(titles, platforms, urls, user_scores, summaries, dates, meta_scores, images, genres, reviews), user_input=user_input, total_pages=total_pages, total_results=total_results)

class MyWhooshSearch(object):
	"""docstring for MyWhooshSearch"""
	def __init__(self):
		super(MyWhooshSearch, self).__init__()

	def search(self, queryEntered, platforms, genres, user_score_from, user_score_to, metacritic_score_from, metacritic_score_to, page, years_from, years_to):
		title = list()
		platform = list()
		genre = list()
		date = list()
		url = list()
		image = list()
		user_score = list()
		meta_score = list()
		summary = list()
		reviews = list()
		num_results = 0
		with self.indexer.searcher() as search:
			# note: the url is searched on based on these fields
			query = MultifieldParser(['FullTitle', 'FullPlatform', 'Userscore', 'Metascore', 'Summary', 'Genres'], schema=self.indexer.schema)

			if (platforms != ""):
				queryEntered = queryEntered + " Platform:"
				platforms = platforms.lower().split()
				if (len(platforms) == 1):
					queryEntered = queryEntered + "'" + platforms[0] + "'"
				else:
					queryEntered = queryEntered + platforms[0]
					for idx, i in enumerate(platforms):
						if (idx != 0):
							queryEntered = queryEntered + " OR '" + i + "'"

			if (genres != ""):
				queryEntered = queryEntered + " Genres:"
				genres = genres.lower().split()
				if (len(genres) == 1):
					queryEntered = queryEntered + "'" + genres[0] + "'"
				else:
					queryEntered = queryEntered + genres[0]
					for idx, i in enumerate(genres):
						if (idx != 0):
							queryEntered = queryEntered + " OR '" + i + "'"

			if (years_from != "" or years_to != ""):
				queryEntered = queryEntered + " Date:["
				platforms = platforms.split()
				if (years_from == ""):
					queryEntered = queryEntered + "TO 'January 1, " + years_to[2:] + "']"
				elif (years_to == ""):
					queryEntered = queryEntered + "'January 1, " + years_from[2:] + "' TO]"  
				else:
					queryEntered = queryEntered + "'January 1, " + years_from[2:] + "' TO '" + "January 1, " + years_to + "']"

			if (user_score_from != "" or user_score_to != ""):
				queryEntered = queryEntered + " Userscore:["
				platforms = platforms.split()
				if (user_score_from == ""):
					queryEntered = queryEntered + "TO " + "{:.1f}".format(float(user_score_to)) + "]"
				elif (user_score_to == ""):
					queryEntered = queryEntered + "{:.1f}".format(float(user_score_from)) + " TO]"  
				else:
					queryEntered = queryEntered + "{:.1f}".format(float(user_score_from)) + " TO " + "{:.1f}".format(float(user_score_to)) + "]"

			if (metacritic_score_from != "" or metacritic_score_to != ""):
				queryEntered = queryEntered + " Metascore:["
				platforms = platforms.split()
				if (metacritic_score_from == ""):
					queryEntered = queryEntered + "TO " + "{:.1f}".format(float(metacritic_score_to)) + "]"
				elif (metacritic_score_to == ""):
					queryEntered = queryEntered + "{:.1f}".format(float(metacritic_score_from)) + " TO]"  
				else:
					queryEntered = queryEntered + "{:.1f}".format(float(metacritic_score_from)) + " TO " + "{:.1f}".format(float(metacritic_score_to)) + "]"

			query = query.parse(queryEntered)
			results = search.search_page(query, int(page), sortedby=["Metascore", "Userscore"], reverse=True)
			total_results = search.search(query, limit=None).scored_length()
			total_pages = math.ceil(total_results/10)

			for x in results:
				title.append(x['FullTitle'])
				platform.append(x['FullPlatform'])
				genre.append(x['FullGenres'])
				date.append(x['Date'])
				url.append(x['Url'])
				image.append(x['Image'])
				user_score.append(x['Userscore'])
				meta_score.append(x['Metascore'])
				summary.append(x['Summary'])
				reviews.append(x['Reviews'])

		return title, platform, url, user_score, summary, date, meta_score, image, genre, page, total_pages, total_results, reviews

	def review_search(self, game_title, user):
		titles = list()
		names = list()
		dates = list()
		user_rev_scores = list()
		reviews = list()
		with self.review_indexer.searcher() as search:
			query = MultifieldParser(['FullTitle', 'Name'], schema=self.review_indexer.schema)
			if (user == 'None'):
				query = query.parse(game_title)
			else:
				query = query.parse(str(user))
			results = search.search(query, limit=None, sortedby='Name')

			for x in results:
				titles.append(x['FullTitle'])
				names.append(x['Name'])
				dates.append(x['Date'])
				user_rev_scores.append(x['User_Rev_Score'])
				reviews.append(x['Review'])

		return names, dates, user_rev_scores, reviews, game_title, titles

	def index(self):
		self.indexer = open_dir("index")
		self.review_indexer = open_dir("reviews_index");

if __name__ == '__main__':
	global mysearch
	mysearch = MyWhooshSearch()
	mysearch.index()
	app.run(debug=True)