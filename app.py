# Code by Mr Aryan Kohli
import os
from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

from sqlalchemy import func
# Initializing the app
app = Flask(__name__)
app.secret_key = 'kohli'

current_dir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(current_dir, "database.sqlite3")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
app.app_context().push()



class User(db.Model):

    __tablename__ = 'User'

    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='User')

class Section(db.Model):
    __tablename__ = 'Section'
    sectionId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sectionName = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    dateCreated = db.Column(db.String(100), nullable=False)

    books = db.relationship('Book', backref='section', lazy=True)

class Book(db.Model):
    __tablename__ = 'Book'
    bookId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author = db.Column(db.String(100), nullable=False)
    bookName = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(100), nullable=False)
    sectionId = db.Column(db.Integer, db.ForeignKey('Section.sectionId'), nullable=False)

class IssuedBooks(db.Model):
    __tablename__ = 'IssuedBooks'

    issued_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    userId = db.Column(db.Integer, db.ForeignKey('User.userId'), nullable=False)
    
    bookId = db.Column(db.Integer, db.ForeignKey('Book.bookId'), nullable=False)
    
    issueDate = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref=db.backref('issued_books', lazy=True))
    book = db.relationship('Book', backref=db.backref('issued_books', lazy=True))


class Rating(db.Model):

    __tablename__ = 'Rating'

    ratingId = db.Column(db.Integer, primary_key=True, autoincrement=True)

    userId = db.Column(db.Integer, db.ForeignKey('User.userId'), nullable=False)
    
    bookId = db.Column(db.Integer, db.ForeignKey('Book.bookId'), nullable=False)
    
    comment = db.Column(db.String, nullable=False)
    user = db.relationship('User', backref=db.backref('ratings', lazy=True))
    book = db.relationship('Book', backref=db.backref('ratings', lazy=True))

class Requests(db.Model):
    __tablename__ = 'Requests'
    requestId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('User.userId'), nullable=False)
    bookId = db.Column(db.Integer, db.ForeignKey('Book.bookId'), nullable=False)

    user = db.relationship('User', backref=db.backref('user_requests', lazy=True))
    book = db.relationship('Book', backref=db.backref('book_requests', lazy=True))

class History(db.Model):
    __tablename__ = 'History'
    historyId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    issuedDate = db.Column(db.DateTime, nullable=False)
    returnDate = db.Column(db.DateTime)
    bookId = db.Column(db.Integer, db.ForeignKey('Book.bookId'), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('User.userId'), nullable=False)
    bookName = db.Column(db.String(100), nullable=False)

    user = db.relationship('User', backref=db.backref('history', lazy=True))
    book = db.relationship('Book', backref=db.backref('history', lazy=True))




@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = User.query.filter_by(username=username, password=password, role='Admin').first()

        if admin:

            return render_template('admindashboard.html')
        else:
            return "Log in failed"
        
@app.route('/displaysection')
def displaysection():
    sections = Section.query.all()
    return render_template('sectionManagement.html', sections = sections)

@app.route('/displaybooks')
def displaybooks():
    sections = Section.query.all()
    section = Section.query.first()
    books = Book.query.all()

    return render_template('userBooks.html', sections = sections, section = section, books = books)

@app.route('/displayrequest')
def displayrequest():
    requests = Requests.query.all()
    return render_template('requestManagement.html', requests = requests)

@app.route('/usersignup', methods=['GET', 'POST'])
def usersignup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User(username= username, password=password)

        db.session.add(user)
        db.session.commit()

        return userlogin()

@app.route('/userlogin', methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password, role='User').first()

        if user:
            session['userId'] = user.userId
            sections = Section.query.all()
            s = sections[0]
            return section(s.sectionId)
        
            
        else:
            return "USER Log in failed"
        

@app.route('/request/<bookId>', methods=['GET', 'POST'])
def request_book(bookId):
    book = Book.query.filter_by(bookId=bookId).first()
    userId = session.get('userId')
    existing_request_count = Requests.query.filter_by(userId=userId).count()
    if existing_request_count >= 50:
        return "Max request limit reached"
    

    request = Requests(userId=userId, bookId=bookId)
    db.session.add(request)
    db.session.commit()
    
    return section(book.sectionId)
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        try:
            s = request.form['search']
            result = Book.query.filter(Book.bookName.ilike(f"%{s}%")).all()
            result2 = Book.query.filter(Book.author.ilike(f"%{s}%")).all()
            result3 = Section.query.filter(Section.sectionName.ilike(f"%{s}%")).all()
            return render_template ('search.html', result=result, result2=result2, result3 = result3, s=s)
        except KeyError:
            # Handle case where 'search' key is missing
            return render_template('search.html', result=[], result2=[], s='')
    else:
        # Handle GET request (if needed)
        return render_template('search.html', result=[], result2=[], s='')

        
@app.route('/section/<sectionId>', methods=['GET', 'POST'])
def section(sectionId):
    sections = Section.query.all()
    section = Section.query.filter_by(sectionId=sectionId).first()

    userId = session.get('userId')
    requests = Requests.query.filter_by(userId=userId).all()
    
    # Create an empty list to store bookIds
    requested_book_ids = []
    # Iterate over requests and collect bookIds
    for req in requests:
        requested_book_ids.append(req.bookId)

    user = User.query.filter_by(userId=userId).first()
    books = Book.query.filter_by(sectionId=sectionId).all()
    issuedBooks = IssuedBooks.query.filter_by(userId=userId).all()
    issued_bookId = []
    for book in issuedBooks:
        issued_bookId.append(book.bookId)
    return render_template('home.html', sections=sections, books=books, section=section, user=user, requests=requests, requested_book_ids=requested_book_ids, issuedBooks=issued_bookId)

        
@app.route('/addSection', methods=['GET', 'POST'])
def addSection():
    if request.method == "POST":
        sectionName = request.form['sectionName']
        description = request.form['description']
        currentDate = datetime.today().date()
        section = Section(sectionName=sectionName, description=description, dateCreated=currentDate)
        db.session.add(section)
        db.session.commit()

        sections = Section.query.all()
        return render_template('sectionManagement.html', sections = sections)
    
@app.route('/addBooks/<sectionId>', methods=['GET', 'POST'])
def addBooks(sectionId):
    section = Section.query.filter_by(sectionId=sectionId).first()
    books = Book.query.filter_by(sectionId=sectionId).all()

    if request.method == 'POST':
        bookName = request.form['bookName']
        author = request.form['author']
        content = request.form['content'] 
        
        book = Book(bookName=bookName, author=author, content=content, sectionId=sectionId)

        db.session.add(book)
        db.session.commit()
        books = Book.query.filter_by(sectionId=sectionId).all()
        
        # Render the template with the updated list of books
        return render_template('books.html', books = books, section = section )

    # Render the template with the initial list of books
    return render_template('books.html', section=section, books=books)

@app.route('/updatesection/<sectionId>', methods=['GET', 'POST'])
def updatesection(sectionId):
    if request.method == 'POST':
        section = Section.query.filter_by(sectionId= sectionId).first()

        section.sectionName = request.form['sectionName']
        section.description = request.form['description']
        db.session.commit() 

        sections = Section.query.all()
        return render_template('sectionManagement.html', sections = sections)

    section = Section.query.filter_by(sectionId=sectionId).first()
    return render_template('updatesection.html', section=section)

@app.route('/rejectrequest/<requestId>')
def rejectrequest(requestId):
        request = Requests.query.filter_by(requestId = requestId).first()
        db.session.delete(request)
        db.session.commit()
        requests = Requests.query.all()
        return render_template('requestManagement.html', requests = requests)


@app.route('/acceptrequest/<requestId>')
def acceptrequest(requestId):
    # Assuming you have a Request model to fetch the userId and bookId
    request_data = Requests.query.get_or_404(int(requestId))

    # Create a new IssuedBooks instance
    new_issued_book = IssuedBooks(
        userId=request_data.userId,
        bookId=request_data.bookId,
        issueDate=datetime.now(),
    )
    db.session.add(new_issued_book)
    db.session.commit()
    return rejectrequest(requestId)

@app.route('/deletebook/<bookId>', methods=['GET', 'POST'])
def deletebook(bookId):
    # Retrieve all reviews for the book
    reviews = Rating.query.filter_by(bookId=bookId).all()

    # Delete each review individually
    for review in reviews:
        db.session.delete(review)

    # Retrieve all requests associated with the book
    book_requests = Requests.query.filter_by(bookId=bookId).all()

    # Delete each request individually
    for request in book_requests:
        db.session.delete(request)
    
    history = History.query.filter_by(bookId = bookId).all()
    for h in history:
        db.session.delete(h)
    # Retrieve the book itself
    book = Book.query.filter_by(bookId=bookId).first()
    sectionId = book.sectionId
    section = Section.query.filter_by(sectionId = sectionId).first()
    # Check if book is not None before attempting to delete
    if book is not None:
        # Delete the book
        db.session.delete(book)
    books = Book.query.filter_by(sectionId = sectionId).all()
    # Commit the changes to the database
    db.session.commit()



    return render_template('books.html', books=books, section= section)



@app.route("/delete/<sectionId>", methods=['GET', 'POST'])
def delete(sectionId):
    section = Section.query.filter_by(sectionId=sectionId).first()
    if section:
        db.session.delete(section)
        db.session.commit()
    sections = Section.query.all()
    return render_template('sectionManagement.html', sections=sections)


@app.route("/displayusermanagement")
def displayusermanagement():
        issuedBooks = IssuedBooks.query.all()
        return render_template("userManagement.html", issuedBooks = issuedBooks)

@app.route("/revokeaccess/<issued_id>")
def revokeaccess(issued_id):
        record = IssuedBooks.query.filter_by(issued_id = issued_id).first()

        userId = record.userId
        bookId = record.bookId
        issueDate = record.issueDate
        returnDate = datetime.now()
        history(issueDate, returnDate, bookId, userId)

        if record:
            db.session.delete(record)
            db.session.commit()
        return (displayusermanagement())


def history(issueDate, returnDate, bookId, userId):
    bookName = Book.query.filter_by(bookId = bookId).first().bookName
    his = History(userId = userId, bookId = bookId, bookName = bookName, issuedDate = issueDate, returnDate = returnDate)
    db.session.add(his)
    db.session.commit()
    return


@app.route("/viewIssuedBook")
def viewIssuedBook():
    userId = session.get('userId')
    entries = IssuedBooks.query.filter_by(userId = userId).all()
    user = User.query.filter_by(userId = userId).first()
    books = Book.query.all()
    history = History.query.filter_by(userId = userId).all()
    time = datetime.now()
    threshold = timedelta(days=7)

    for e in entries:
        print(f"Difference: {e.issueDate - time}")
        if (time - e.issueDate) > threshold:
            print("Garari")
            return returnbook(e.issued_id)
        
    return render_template("userIssuedbooks.html" , entries= entries, user= user, books = books, history = history)

@app.route("/userreturnbook/<issued_id>")
def returnbook(issued_id):  
        record = IssuedBooks.query.filter_by(issued_id = issued_id).first()

        userId = record.userId
        bookId = record.bookId
        issueDate = record.issueDate
        returnDate = datetime.now()
        history(issueDate, returnDate, bookId, userId)

        if record:
            db.session.delete(record)
            db.session.commit()
        return (viewIssuedBook())

@app.route('/review', methods=['GET', 'POST'])
def review():
    if request.method == 'POST':
        review = request.form['review']
        userId = session.get('userId')
        bookId = int(request.form['bookId'])
        review = Rating(userId = userId, comment = review, bookId = bookId)
        db.session.add(review)
        db.session.commit()
    return (viewIssuedBook())


@app.route('/viewreviews/<bookId>')
def viewreviews(bookId):
    reviews = Rating.query.filter_by(bookId = bookId).all()
    book = Book.query.filter_by(bookId = bookId).first()
    return render_template("viewreview.html", book = book, reviews = reviews)

@app.route('/stat')
def stat():
    stats = History.query.all()
    return render_template('stat.html', stats= stats)
if __name__ == '__main__':
    app.run(debug=True)