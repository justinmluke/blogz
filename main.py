from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body
     

@app.route('/blogs', methods=['GET'])
def index():

    blogs = Blog.query.all()
    return render_template("blogs.html", title="My Blogs", blogs=blogs)

@app.route('/newpost')
def new_post():
    return render_template("new_post.html", title="Add New Post")    

@app.route('/newpost', methods=["POST"])
def add_post():
   
    blog_title = request.form['blog-title']
    blog_body = request.form['blog-body']

    title_error = ""
    body_error = ""

    if blog_title == "":
        title_error = "Please enter a valid title"

    if blog_body == "":
        body_error = "Please enter a valid post"

    if not title_error and not body_error:
        new_blog = Blog(blog_title, blog_body)
        db.session.add(new_blog)
        db.session.commit()
        return render_template("blog.html", blog=new_blog)
    else:
        return render_template("new_post.html", title_error=title_error, body_error=body_error, title="Add New Post", blog_title=blog_title, blog_body=blog_body)            

@app.route('/blog')
def display_blog():

    blog_id = request.args.get('id')
    blog = Blog.query.get(blog_id)

    return render_template('blog.html', blog=blog)

app.run()