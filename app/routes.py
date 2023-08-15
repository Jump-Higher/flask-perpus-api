from app import app
from app.controllers import user, auth, authors, bookshelves, categories, publishers, roles
@app.route('/')
def home():
    return 'This is Home Page for Perpustakaan App'

app.route('/login', methods = ['POST'])(auth.login)

# Users
app.route('/register', methods = ['POST'])(user.register)
app.route('/user/<id>', methods = ['GET'])(user.user)
app.route('/user/update/<id>', methods = ['PATCH'])(user.update_user)
app.route('/users', methods = ['GET'])(user.list_user)

# Roles
app.route('/role/create', methods = ['POST'])(roles.create_role)
app.route('/role/<id>', methods = ['GET'])(roles.role)
app.route('/role/update/<id>', methods = ['PATCH'])(roles.update_role)
app.route('/roles', methods = ['GET'])(roles.roles)

# Authors
app.route('/author/create', methods = ['POST'])(authors.create_author)
app.route('/author/<id>', methods = ['GET'])(authors.author)
app.route('/author/update/<id>', methods = ['PATCH'])(authors.update_author)
app.route('/authors', methods = ['GET'])(authors.authors)

# Publishers
app.route('/publisher/create', methods = ['POST'])(publishers.create_publisher)
app.route('/publisher/<id>', methods = ['GET'])(publishers.publisher)
app.route('/publisher/update/<id>', methods = ['PATCH'])(publishers.update_publisher)
app.route('/publishers', methods = ['GET'])(publishers.publishers)

# Bookshelves
app.route('/bookshelf/create', methods = ['POST'])(bookshelves.create_bookshelf)
app.route('/bookshelf/<id>', methods = ['GET'])(bookshelves.bookshelf)
app.route('/bookshelf/update/<id>', methods = ['PATCH'])(bookshelves.update_bookshelf)
app.route('/bookshelves', methods = ['GET'])(bookshelves.bookshelves)

# Categories
app.route('/category/create', methods = ['POST'])(categories.create_category)
app.route('/category/<id>', methods = ['GET'])(categories.category)
app.route('/category/update/<id>', methods = ['PATCH'])(categories.update_category)
app.route('/categories', methods = ['GET'])(categories.categories)



