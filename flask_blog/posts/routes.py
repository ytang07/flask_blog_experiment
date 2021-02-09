from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from flask_blog import db
from flask_blog.models import Post
from flask_blog.posts.forms import PostForm

posts = Blueprint('posts', __name__)

# create a blog post functionality
# requires that a user is logged in
@posts.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    # grab the form we made for the post
    form = PostForm()
    
    # ensure that the post data is all valid and then save to the db
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template("create_post.html", title = "New Post", form = form, legend='New Post')

# view a post
# basically just check if the post id exists and load it or a 404
@posts.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title = post.title, post = post)

# updates a post
# requires that the user is logged in
@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    # make sure the post exists before we can update it
    post = Post.query.get_or_404(post_id)

    # make sure that the author of the post is the one updating it
    if post.author != current_user:
        abort(403)

    # load our post form
    form = PostForm()

    # if all the info checks out, we can save it in the db
    # if we're loading the page, prepopulate the values of the fields
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated!", 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template("create_post.html", title = "Update Post", form = form, legend='Update Post')

# delete a post
# requires the user that owns that post to be logged in
@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    # check if the post exists, return a 404 if it doesn't
    post = Post.query.get_or_404(post_id)
    
    # check that the right user is logged in
    if post.author != current_user:
        abort(403)
    
    # delete post
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted!", 'success')
    return redirect(url_for('main.home'))