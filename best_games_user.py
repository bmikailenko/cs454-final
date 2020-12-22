from bs4 import BeautifulSoup
import requests as req
import csv
import time
import pandas as pd
import os.path

#make a folder named 'data'
if not os.path.exists('data'):
        os.mkdir('data')

#remove previous data if it exists
if os.path.exists('data/best-User-games.csv'):
    os.remove('data/best-User-games.csv')

#initialize a list which will contain our tuples
database=[]

#which page to scrape up to (max 180)
range_to = 20

for page in range(0,range_to):

    print("scraping page " + str(page+1) + "/" + str(range_to) + "...")

    #grab our metacritic page
    url='https://www.metacritic.com/browse/games/score/metascore/all/all/filtered?page='+str(page)
    user_agent = {'User-agent': 'Mozilla/5.0'}
    r = req.get(url, headers =user_agent)

    #parse the html code from our given link
    soup = BeautifulSoup(r.text, 'html.parser')
    image_wrap_data = soup('td', class_='clamp-image-wrap')

    #grab everything under the clamp-summary-wrap header from HTML
    #this is where all of the text is located, num, title, score, platform, summary, url
    #idx is the row count
    #i is the data from soup for each row
    for idx, i in enumerate(soup('td', class_='clamp-summary-wrap')):

        print(idx + (page * 100));

        # game rank on the list
        num=i.find('span' , class_='title numbered').text.strip()

        # game title
        title=i.find('a', class_='title').text.strip()

        # game platform
        platform=i.find('span' , class_='data').text.strip()

        # game release date
        release_date=i.find('div', class_='clamp-details').select('span')[2].text.strip()

        # game summary
        summary=i.find('div' , class_='summary').text.strip()

        # game userscore
        #       note:  div classes change depending on userscore
        #              find returns None if looking for class that doesn't exist
        #              need to consider all possible options
        userscore=i.find('div' , class_='metascore_w user large game positive')
        if userscore is None:
            userscore=i.find('div' , class_='metascore_w user large game mixed')
        if userscore is None:
            userscore=i.find('div' , class_='metascore_w user large game negative')
        if userscore is None:
            userscore = 'tbd';
        if (userscore != 'tbd'):
            userscore = userscore.text.strip()

        # scrape metascore
        #       note: same case as userscore
        metascore=i.find('div' , class_='metascore_w large game positive')
        if metascore is None:
            metascore=i.find('div' , class_='metascore_w large game mixed')
        if metascore is None:
            metascore=i.find('div' , class_='metascore_w large game negative')
        metascore = metascore.text.strip()

        # scrape game image
        image = image_wrap_data[idx].find('img')['src']

        # grab metacritic page for the current game being scraped
        game_page = image_wrap_data[idx].find('a')['href']

        if (game_page):

            # request the games 'summary' page
            game_page_request = req.get("https://www.metacritic.com" + game_page, headers=user_agent)

            if (game_page_request):

                # parse the games 'summary' page 
                game_page_soup = BeautifulSoup(game_page_request.text, 'html.parser')

                if (game_page_soup):

                    # srape game genres

                    # get the game genres from the games metacrtic page
                    game_page_genres_table = game_page_soup('li', class_="summary_detail product_genre")[0]
                    if (game_page_genres_table):
                        game_page_genres_list = game_page_genres_table.find_all('span', class_="data")
                        if (game_page_genres_list):
                            # organize genres in a string seperated by a comma
                            genres = ', '.join([str(elem.text.strip()) for elem in game_page_genres_list])

            # request the games 'user reivews' page
            review_page_request = req.get("https://www.metacritic.com" + game_page + "/user-reviews?page=0", headers=user_agent)

            if (review_page_request):

                # parse the games 'user reviews' page
                review_page_soup = BeautifulSoup(review_page_request.text, 'html.parser')

                # list of reviews
                reviews = []

                for i in review_page_soup.find_all('div', class_='review_content', limit=30):
                    if i.find('div', class_='name') == None:
                        break 

                    # reviewer name
                    name = i.find('div', class_='name').find('a')
                    if (name == None):
                        name=i.find('div', class_='name').find('span')
                    name = name.text.strip()

                    # review date
                    date = i.find('div', class_='date').text.strip()

                    # review score
                    user_rev_score = i.find('div', class_='review_grade').find_all('div')[0].text.strip()
                    
                    # review
                    if i.find('span', class_='blurb blurb_expanded'):
                        review = i.find('span', class_='blurb blurb_expanded')
                    if i.find('div', class_='review_body'):
                        review = i.find('div', class_='review_body').find('span')
                    if (review == None):
                        review = 'None';
                    if (review != 'None'):
                        review = review.text.strip()
            
                    # append to list of reviews in dictionary format: (name, date, user_rev_score, review)        
                    reviews.append({'name': name, 'date': date, 'user_rev_score': user_rev_score, 'review': review})
        

        # bigfix: case when genres isn't there
        if (genres == None):
            genres = ""

        #create our database, which is a list of tuples
        database.append((num, title, platform, release_date, genres, summary, userscore, metascore, image, game_page, reviews))

#and now give our data a spreadsheet structure similar to an SQL table
#arrange into columns by date of claim, claim, truth, and URL for the factcheck
#we start by creating the constructor using the pandas built-in DataFrame
print("finished scraping, adding to csv...")
df = pd.DataFrame(database, columns=['num','title', 'platform', 'release date', 'genres', 'summary', 'user score', 'meta score','image', 'url', 'reviews'])

#now posit our data frame into a CSV file
df.to_csv('./data/best-User-games.csv', index=False, encoding='utf-8')
print("done!")
