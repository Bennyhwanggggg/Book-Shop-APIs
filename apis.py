from flask import Flask, jsonify, url_for
from flask_restful import reqparse
from mongoengine import connect, StringField, Document, EmbeddedDocument, IntField, FloatField, DateTimeField


app = Flask(__name__)


connect(host='mongodb://candidatebenny:bcs2018@ds119350.mlab.com:19350/bcstechapitask')


# Book data structure, tags are one word with no space only. ID is the name of the book with no space and all lower case.
class Book(Document):
    id = StringField(required=True, primary_key=True)
    name = StringField(required=True)
    price = FloatField(required=True)
    author = StringField(required=True)
    tag = StringField(required=True)
    year = IntField(required=True)

    def __init__(self, id, name, price, author, tag, year, *args, **values):
        super().__init__(*args, **values)
        self.id = id
        self.name = name
        self.price = price
        self.author = author
        self.tag = tag
        self.year = year


# user can upload a book's data into database
# Usage: Have the below 5 parameters in the correct format in POST request body
@app.route('/new', methods=['POST'])
def addnewbook():
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str)
    parser.add_argument('price', type=float)
    parser.add_argument('author', type=str)
    parser.add_argument('tag', type=str)
    parser.add_argument('year', type=str)
    args = parser.parse_args()
    name = args.get('name')
    price = args.get('price')
    author = args.get('author')
    tag = args.get('tag')
    year = args.get('year')
    if not name or not price or not author or not tag or not year:
        return jsonify(error_message='Insufficient information provided for upload.'), 400
    id = name.replace(' ', '').lower()
    data = Book(id, name, price, author, tag, year)
    data.save()
    return jsonify(message='success'), 201


# return a list of book names and their details
@app.route('/all', methods=['GET'])
def getall():
    booklist = [book for book in Book.objects]
    result = []
    for b in booklist:
        bk = dict()
        bk['name'] = b.name
        bk['year'] = b.year
        bk['tag'] = b.tag
        bk['author'] = b.author
        bk['price'] = b.price
        result.append(bk)
    return jsonify(result), 200


# delete a book by it's name/id. If a book is not in database, still return success and 200 as nothing will happen.
@app.route('/book/<id>', methods=['DELETE'])
def deletebook(id):
    id = id.replace(' ', '').lower()
    Book.objects(id=id).delete()
    return jsonify(message='Delete success'), 200


# get books by filter. Filter will support tag, price between entered range, author, year
# Usage: Have one or more of the fields as query parameters
@app.route('/book', methods=['GET'])
def getbook():
    parser = reqparse.RequestParser()
    parser.add_argument('tag', type=str)
    parser.add_argument('pricestart', type=float)
    parser.add_argument("priceend", type=float)
    parser.add_argument("year", type=str)
    args = parser.parse_args()
    tag = args.get('tag')
    pricestart = args.get('pricestart')
    priceend = args.get('priceend')
    year = args.get('year')
    bookwithtags, bookwithinprice, bookwithyear = [], [], []
    if tag:
        bookwithtags = [book for book in Book.objects(tag=tag)]
    if pricestart and priceend:
        if bookwithtags:
            bookwithinprice = [book for book in bookwithtags if pricestart <= book.price <= priceend]
        else:
            bookwithinprice = [book for book in Book.objects() if pricestart <= book.price <= priceend]
    if year:
        if bookwithtags and bookwithinprice:
            bookwithyear = [book for book in bookwithyear if book.year == year]
        elif bookwithinprice:
            bookwithyear = [book for book in bookwithinprice if book.year == year]
        elif bookwithtags:
            bookwithyear = [book for book in bookwithtags if book.year == year]
        else:
            bookwithyear = [book for book in Book.objects(year=year)]

    if not bookwithtags and not bookwithinprice and not bookwithyear:
        return jsonify(message='Invalid input or no entry found'), 200
    if bookwithyear:
        resultquery = bookwithyear
    elif bookwithinprice:
        resultquery = bookwithinprice
    else:
        resultquery = bookwithtags

    result = []
    for b in resultquery:
        bk = dict()
        bk['name'] = b.name
        bk['year'] = b.year
        bk['tag'] = b.tag
        bk['author'] = b.author
        bk['price'] = b.price
        result.append(bk)
    return jsonify(result), 200


# tag rename
# Usage: /book/bookid then the new tag name inside PUT request body as 'tag': [new tag name here]
@app.route('/book/<id>', methods=['PUT'])
def renametag(id):
    parser = reqparse.RequestParser()
    parser.add_argument('tag', type=str)
    args = parser.parse_args()
    tag = args.get('tag')
    if not tag:
        return jsonify(message='No input'), 400
    targetbook = Book.objects(id=id)
    if not targetbook:
        return jsonify(message='Book not found'), 200
    targetbook.update(tag=tag)
    return jsonify(message='Success'), 200


if __name__ == "__main__":
    app.run()

