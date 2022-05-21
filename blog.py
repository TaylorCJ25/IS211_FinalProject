import sqlite3
from flask import Flask, request, redirect, url_for, render_template, flash, session, abort
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
          session['username'] = request.form['username']
          return redirect(url_for('login'))
    if 'username' in session:
	    return redirect('/post')
    else:
        return render_template('login.html', message='You are not logged in')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)

    return redirect(url_for('login'))


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/post')
def post():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('post.html', posts=posts)


@app.route('/<int:post_id>')  # allos link of posts to be visable
def posts(post_id):
    post = get_post(post_id)
    return render_template('posts.html', post=post)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('post'))
    return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('post'))

    return render_template('edit.html', post=post)


@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('post'))


if __name__ == '__main__':
    app.debug = True
    app.run()
