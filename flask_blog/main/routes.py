from flask import render_template, request, Blueprint
from flask_blog.models import Post

main = Blueprint('main', __name__)

# home page should load a list of the blog posts
# paginate so there's only 5 posts on each page
@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("home.html", posts = posts)

# about page is just a placeholder for now
@main.route("/about")
def about():
    return render_template("about.html", title = "About")