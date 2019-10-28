import requests as _req
import sqlalchemy as sqla

from bs4 import BeautifulSoup


def call_procedure(function_name, params):
    connection = sqla.create_engine('mysql://root:@localhost/hotel-reviews?charset=utf8').raw_connection()
    try:
        cursor = connection.cursor()
        cursor.callproc(function_name, params)
        results = list(cursor.fetchall())
        cursor.close()
        connection.commit()
        return results
    finally:
        connection.close()


if __name__ == "__main__":
    rev_url = input('Enter tripadvisor hotel url here:')

    reviews = _req.get(rev_url)

    _page_content = BeautifulSoup(reviews.content, 'html.parser')

    reviews_list = []
    for review in _page_content.find_all('q'):
        review_content = review.getText()

        positive = int(
            input(review_content + '\n is the above content a positive review or not? (1 = positive, 0 = negative)')
        )
        positive = 1 if positive == 1 else 0

        call_procedure('addReview', [review_content, -1, positive])

    print('all done')


