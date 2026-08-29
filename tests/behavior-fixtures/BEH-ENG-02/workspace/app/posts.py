"""Post records and their public URLs."""

POSTS = [
    {"id": 7, "title": "Hello, World!"},
    {"id": 12, "title": "Release  Notes: v2"},
]


def get_post(post_id):
    for post in POSTS:
        if post["id"] == post_id:
            return post
    return None


def post_url(title, post_id):
    """Public URL for a post: /posts/<id>/<url-safe title>.

    TODO: implement.
    """
    raise NotImplementedError
