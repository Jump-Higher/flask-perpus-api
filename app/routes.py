from app import app
from app.controllers import user
@app.route('/')
def home():
    return 'This is Home Page for Perpustakaan App'

app.route('/register', methods = ['POST'])(user.register)