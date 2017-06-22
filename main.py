from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'eeAtvm8N^XHA66gX'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40))
    body = db.Column(db.String(120))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, author):
        self.title = title
        self.body = body
        self.author = author

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40))
    password = db.Column(db.String(40))
    blogs = db.relationship("Blog", backref="author")

    def __init__(self, username, password):
        self.username = username
        self.password = password



@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        
        if username == "":
            flash("Please enter a valid username", 'error')
        else:
            if len(username) < 3 or len(username) > 20:
                flash('Username must be between 3 and 20 charcters', 'error')
            else:
                if " " in username:
                    flash("Username cannot contain any spaces", 'error')
                else:
                    if password == "":
                        flash("Please enter a valid password", 'error')
                    else:
                        if len(password) < 3 or len(password) > 20:
                            flash("Password must be between 3 and 20 characters", 'error')
                        else:
                            if " " in password:
                                flash("Password cannot contain any spaces", 'error')
                            else:            
                                if not existing_user and password == verify:
                                    new_user = User(username, password)
                                    db.session.add(new_user)
                                    db.session.commit()
                                    session['username'] = username
                                    return redirect('/newpost')
                                else:
                                    flash('User already exist', 'error')    

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else: 
            flash('User password incorrect or user does not exist', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    flash('Logged Out!')
    return redirect('/blog')

@app.route('/newpost')
def new_post():
    return render_template("new_post.html", title="Add New Post")    

@app.route('/newpost', methods=["POST"])
def add_post():
   
    blog_title = request.form['blog-title']
    blog_body = request.form['blog-body']
    author = User.query.filter_by(username=session['username']).first() 
    
    title_error = ""
    body_error = ""

    if blog_title == "":
        title_error = "Please enter a valid title"

    if blog_body == "":
        body_error = "Please enter a valid post"

    if not title_error and not body_error:
        new_blog = Blog(blog_title, blog_body, author)
        db.session.add(new_blog)
        db.session.commit()
        return render_template("blog.html", blog=new_blog, user=author)
    else:
        return render_template("new_post.html", title_error=title_error, body_error=body_error, title="Add New Post", blog_title=blog_title, blog_body=blog_body)            

@app.route('/blog')
def blog(): 

    if request.args.get('id'):
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        user = User.query.filter_by(id=blog.author_id).first()
        return render_template('blog.html', blog=blog, user=user)
    else:
        if request.args.get('user'):
            user_id = request.args.get('user')
            user = User.query.get(user_id)
            blogs = Blog.query.filter_by(author_id=user_id).all()
            return render_template('singleUser.html', user=user, blogs=blogs)
        else:
            blogs = Blog.query.all()
            return render_template("blogs.html", title="All Blogs", blogs=blogs)


if __name__ == '__main__':
    app.run()