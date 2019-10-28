import pandas as pd
import sqlalchemy as sqla


def call_procedure(function_name, params):
    connection = sqla.create_engine(
        'mysql://root:@localhost/hotel-reviews?charset=utf8').raw_connection()
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

    reviews = pd.read_csv('src/reviews.csv')

    negative_df = reviews.loc[:,["Negative_Review", "Review_Total_Negative_Word_Counts"]]
    negative_df["positive"] = 0
    negative_df = negative_df.rename(columns={
        "Negative_Review": "review",
        "Review_Total_Negative_Word_Counts": "word_count"
    })

    positive_df = reviews.loc[:,["Positive_Review", "Review_Total_Positive_Word_Counts"]]
    positive_df["positive"] = 1
    positive_df = positive_df.rename(columns={
        "Positive_Review": "review",
        "Review_Total_Positive_Word_Counts": "word_count"
    })

    reviews_df = pd.concat([negative_df, positive_df]).reset_index(drop=True)

    no_empty = reviews_df

    # Remove the empty reviews
    no_empty = no_empty[no_empty.word_count != 0]
    # reset the index
    no_empty = no_empty.reset_index(drop=True)

    for _i, _v in no_empty.iterrows():
        call_procedure('addReview', [_v['review'], _v['positive']])

