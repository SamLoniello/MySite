from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from flask_sqlalchemy import SQLAlchemy
from flask_frozen import Freezer  # Import Freezer from flask_frozen
from datetime import datetime
import os

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'mysecretkey')
app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD', 'PA$$word01')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
freezer = Freezer(app)  # Initialize Freezer

# Models
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    lastmod = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Poem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    lastmod = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Routes
@app.route('/')
@app.route('/about.html')  # Updated
def about():
    last_login_time = session.get('last_login_time', 'Never')
    return render_template('about.html', last_login_time=last_login_time)

@app.route('/poems.html')  # Updated
def poems_page():
    poems = Poem.query.all()
    return render_template('poems.html', poems=poems)

@app.route('/blog.html')  # Updated
def blog():
    posts = Post.query.all()
    return render_template('blog.html', posts=posts)

@app.route('/projects.html')  # Updated
def projects():
    return render_template('projects.html')

# Login Route
@app.route('/login.html', methods=['GET', 'POST'])  # Updated
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            session['last_login_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Incorrect password. Try again.', 'danger')
    return render_template('login.html')

# Logout Route
@app.route('/logout.html', methods=['GET', 'POST'])  # Updated
def logout():
    session.pop('logged_in', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

# Admin Route
@app.route('/admin.html', methods=['GET', 'POST'])  # Updated
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content'].replace('\n', '<br>')
        item_type = request.form['type']

        if item_type == 'poem':
            new_item = Poem(title=title, content=content)
        else:
            new_item = Post(title=title, content=content)

        db.session.add(new_item)
        db.session.commit()
        flash('Content added successfully!', 'success')
        return redirect(url_for('admin'))

    posts = Post.query.all()
    poems = Poem.query.all()
    return render_template('admin.html', posts=posts, poems=poems)


# Delete routes
@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/delete_poem/<int:poem_id>', methods=['POST'])
def delete_poem(poem_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    poem = Poem.query.get_or_404(poem_id)
    db.session.delete(poem)
    db.session.commit()
    flash('Poem deleted successfully!', 'success')
    return redirect(url_for('admin'))

# Dynamic Sitemap Route
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    static_urls = [
        {'loc': url_for('about', _external=True), 'lastmod': '2024-11-02', 'changefreq': 'monthly'},
        {'loc': url_for('poems_page', _external=True), 'lastmod': '2024-11-02', 'changefreq': 'weekly'},
        {'loc': url_for('blog', _external=True), 'lastmod': '2024-11-02', 'changefreq': 'weekly'},
        {'loc': url_for('projects', _external=True), 'lastmod': '2024-11-02', 'changefreq': 'monthly'}
    ]

    posts = Post.query.all()
    poems = Poem.query.all()

    sitemap_xml = render_template('sitemap_template.xml', static_urls=static_urls, posts=posts, poems=poems)
    return Response(sitemap_xml, mimetype='application/xml')


# Freezer configuration for dynamic routes
@freezer.register_generator
def blog():
    for post in Post.query.all():
        yield {'post_id': post.id}

@freezer.register_generator
def poems_page():
    for poem in Poem.query.all():
        yield {'poem_id': poem.id}

# Main execution
if __name__ == '__main__':
    freezer.freeze()  # Runs the freeze process to create static files
    app.run(debug=True)
