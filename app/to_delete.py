from app.comments import store_comments_datastore
from app.comments import Comment

my_comment = Comment(
    transaction_id="123",
    survey_id="123",
    period="123",
    zip_name="123",
    encrypted_data="123"
)


store_comments_datastore(my_comment)
