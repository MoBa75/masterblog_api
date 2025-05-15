from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime

app = Flask(__name__)
CORS(app)

SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post.",
     "author": "Admin", "date": "2023-06-01"},
    {"id": 2, "title": "Second post", "content": "This is the second post.",
     "author": "Editor", "date": "2023-06-02"},
]


def create_new_id():
    """
    Creates a new unique ID for a blog entry,
    fills in missing ID numbers.
    :return: A unique ID numer as integer.
    """
    id_lst = [int(post["id"]) for post in POSTS if "id" in post
              and str(post.get("id", "")).isdigit()]
    new_id = next(num for num in range(1, len(POSTS) + 2) if num not in id_lst)
    return new_id


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    """
    With the POST method, creates and saves a new blog entry from user input.
    With the GET method, show all posts. Posts can be sorted by title, content,
    author and date in ascending and descending order. Handles errors.
    """
    if request.method == 'POST':
        new_id = create_new_id()
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")
        author = data.get("author", "Unknown")
        date_str = data.get("date", datetime.today().strftime("%Y-%m-%d"))
        if not title or not content:
            return jsonify({"Error": "Title and content needed!"}), 400
        new_post = {"id": new_id,
                    "title": title,
                    "content": content,
                    "author": author,
                    "date": date_str
                    }
        POSTS.append(new_post)
        return jsonify(new_post), 201

    if request.method == 'GET':
        sort_field = request.args.get('sort')
        direction = request.args.get('direction', 'asc')

        if sort_field:
            if sort_field not in ['title', 'content', 'author', 'date']:
                return jsonify({
                    "Error": "Invalid sort field. Use 'title', "
                             "'content', 'author' or 'date'."}), 400
            if direction not in ['asc', 'desc']:
                return jsonify({"Error": "Invalid direction. Use 'asc' or 'desc'."}), 400

            reverse = direction == 'desc'
            if sort_field == 'date':
                sorted_posts = sorted(POSTS, key=lambda post: datetime.strptime(
                    post.get('date', '1900-01-01'), "%Y-%m-%d"), reverse=reverse)
            else:
                sorted_posts = sorted(POSTS, key=lambda post: post.get(sort_field, "").lower(),
                                      reverse=reverse)
            return jsonify(sorted_posts), 200
    return jsonify(POSTS), 200


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Deletes a blog entry based on the id, handles errors.
    :param post_id: Id of the post to be deleted as integer
    """
    if request.method == 'DELETE':
        for index, post in enumerate(POSTS):
            if post["id"] == post_id:
                POSTS.pop(index)
                return jsonify({"message": f"Post with id {post_id} "
                                           f"has been deleted successfully."}), 200
        return jsonify({"Error": f"Post with id {post_id} not found."}), 404


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Updates title, content, author and / or date of a blog post based on the id, handles errors.
    :param post_id: Id of the post to be updated as integer
    """
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    author = data.get("author")
    date_str = data.get("date")

    if not title or not content:
        return jsonify({"Error": "Title and content needed!"}), 400

    for post in POSTS:
        if post["id"] == post_id:
            post["title"] = title
            post["content"] = content
            post["author"] = author
            post["date"] = date_str
            return jsonify(post), 200
    return jsonify({"Error": f"Post with id {post_id} not found."}), 404


@app.route('/api/posts/search', methods=['GET'])
def search_post():
    """
    Filters the posts based on the users search term(s) in the title,
    content, author and date areas, which are then displayed.
    """
    title = request.args.get("title", "")
    content = request.args.get("content", "")
    author = request.args.get("author", "")
    date = request.args.get("date", "")
    return jsonify([
        post for post in POSTS
        if ((title and title.lower() in post["title"].lower())
            or (content and content.lower() in post["content"].lower())
            or (author and author.lower() in post["author"].lower())
            or (date and date.lower() in post["date"].lower()))
    ]), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
