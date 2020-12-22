from whoosh import fields, index
from whoosh.qparser import QueryParser
from whoosh.index import open_dir
import os.path
from openpyxl import load_workbook
import csv
import codecs

# Function builds a Woosh index over the three .xlsx files
def buildIndex():
    print("Building index...")

    # Create Schema
    schema = fields.Schema(PrimaryKey=fields.ID,
                        Key=fields.ID,
                        Title=fields.KEYWORD,
                        Platform=fields.KEYWORD,
                        Genres=fields.KEYWORD,
                        Date=fields.TEXT(stored=True),
                        FullTitle=fields.TEXT(stored=True),
                        FullPlatform=fields.TEXT(stored=True),
                        FullGenres=fields.TEXT(stored=True),
                        Summary=fields.TEXT(stored=True),
                        Userscore=fields.TEXT(stored=True),
                        Metascore=fields.TEXT(stored=True),
                        Image=fields.TEXT(stored=True),
                        Url=fields.TEXT(stored=True),
                        Reviews=fields.TEXT(stored=True))

    # Create Schema
    reviews_schema = fields.Schema(PrimaryKey=fields.ID,
                        Key=fields.ID,
                        Title=fields.KEYWORD,
                        FullTitle=fields.TEXT(stored=True),
                        Image=fields.TEXT(stored=True),
                        Name=fields.TEXT(stored=True),
                        Date=fields.TEXT(stored=True),
                        User_Rev_Score=fields.TEXT(stored=True),
                        Review=fields.TEXT(stored=True))

    # Create the Whoosh index and Whoosh writer object
    indexname = "index"
    if not os.path.exists(indexname):
        os.mkdir(indexname)
    ix = index.create_in(indexname, schema)
    ix = index.open_dir(indexname)
    writer = ix.writer()

    # add documents to Whoosh writer objects
    print("(1/6): Building List")
    addDocuments('./data/best-User-games.csv', 2001, writer)

    # commit added documents to index
    print("(2/6): Writing Index")
    writer.commit()

    print("(3/6): Finished Building Index")

    # Create the Whoosh index and Whoosh writer object for reviews
    indexname = "reviews_index"
    if not os.path.exists(indexname):
        os.mkdir(indexname)
    ix = index.create_in(indexname, reviews_schema)
    ix = index.open_dir(indexname)
    writer = ix.writer()

    # add documents to Whoosh writer objects
    print("(4/6): Building Reviews List")
    addDocumentsReviews('./data/best-User-games.csv', 2001, writer)

    # commit added documents to index
    print("(5/6): Writing Reviews Index")
    writer.commit()

    print("(6/6): Finished Building Reviews Index\n")

# function adds 'filename'.csv document to the writer
def addDocuments(filename, maxRows, writer):

    # open the csv
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        # ignore header
        next(reader)

        # through each row in the csv
        for idx, row in enumerate(reader):

            # add a document to the index
            writer.add_document(PrimaryKey=str(idx), 
                                Key=str(idx) + "-"+ str(row[0]), 
                                Title=str(row[1]).lower(), 
                                FullTitle=str(row[1]), 
                                Platform=str(row[2]).lower(), 
                                FullPlatform=str(row[2]), 
                                Date=str(row[3]),
                                Genres=str(row[4].replace(',','').lower()), 
                                FullGenres=str(row[4]), 
                                Summary=str(row[5]), 
                                Userscore=str(row[6]), 
                                Metascore=str(row[7]), 
                                Image=str(row[8]), 
                                Url=str(row[9]),
                                Reviews=str(row[10]))


# function adds 'filename'.csv document to the writer
def addDocumentsReviews(filename, maxRows, writer):

    # open the csv
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        # ignore header
        next(reader)

        # through each row in the csv
        for idx, row in enumerate(reader):

            # review data is an array
            #   each element in the array is a dict, 
            #   ({name, date, user_rev_score, review})
            review_data = eval(str(row[10]))

            # for each review
            for i in range(len(review_data)):

                # add a review of a game to the index
                writer.add_document(PrimaryKey=str(idx) + "-" + str(i), 
                                    Key=str(idx) + "-" + str(i) + "-" + str(row[0]), 
                                    Title=str(row[1]).lower(), 
                                    FullTitle=str(row[1]), 
                                    Image=str(row[8]),
                                    Name=str(review_data[i]['name']),
                                    Date=str(review_data[i]['date']),
                                    User_Rev_Score=str(review_data[i]['user_rev_score']),
                                    Review=str(review_data[i]['review']))

def main():
    buildIndex()

main()
