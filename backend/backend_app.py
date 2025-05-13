from flask import Flask, jsonify, request, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import redirect

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def create_new_id():
    """
    Creates a new unique ID for a blog entry,
    fills in missing ID numbers.
    :return: A unique ID numer as integer.
    """
    id_lst = [int(post["id"]) for post in POSTS if "id" in post
              and str(post.get("id", "")).isdigit()]
    new_id = next(num for num in range(1, len(POSTS)+2) if num not in id_lst)
    return new_id


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    if request.method == 'POST':
        new_id = create_new_id()
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")
        if not title or not content:
            return jsonify({"Error": "Title and content needed!"})
        new_post = {"id": new_id,
                    "title": title,
                    "content": content
                    }
        POSTS.append(new_post)
        return jsonify(new_post)
    return jsonify(POSTS)


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    for index, post in enumerate(POSTS):
        if post["id"] == post_id:
            POSTS.pop(index)
            return jsonify({"message": f"Post with id {post_id} has been deleted successfully."})
    return jsonify({"Error": f"Post with id {post_id} not found."})




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5004, debug=True)
