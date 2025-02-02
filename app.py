import os
import json
import redis
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_admin import Admin
from flask_admin.contrib.pymongo import ModelView
from flask_ckeditor import CKEditor
from googletrans import Translator
from flask_wtf import FlaskForm
from wtforms import StringField
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config.update({
    "SECRET_KEY": os.getenv("SECRET_KEY"),  # Security key for the app
    "MONGO_URI": os.getenv("MONGO_URI"),  # Database connection URI
    "CKEDITOR_PKG_TYPE": 'full'  # Enable full CKEditor package
})

# Connect to MongoDB
db = PyMongo(app).db.faqs

# Enable CKEditor (rich text editor)
ckeditor = CKEditor(app)

# Set up admin panel
admin = Admin(app)

# Define a form for FAQs
class FAQForm(FlaskForm):
    question = StringField('Question')
    answer = StringField('Answer')

# Define admin panel view for FAQs
class FAQModelView(ModelView):
    column_list = ('question', 'answer')  # Show only these columns
    def scaffold_form(self):
        return FAQForm

admin.add_view(FAQModelView(db, 'FAQs'))

# Initialize translator and cache
translator = Translator()
cache = redis.Redis(
    host=os.getenv("REDIS_HOST"),  # Redis server host
    port=int(os.getenv("REDIS_PORT")),  # Redis server port
    decode_responses=True  # Decode responses into readable format
)

# Function to translate FAQs into all languages
def save_translations(faq):
    languages = translator.LANGUAGES.keys()  # Get all available languages
    for lang in languages:
        faq[f'question_{lang}'] = translator.translate(faq['question'], dest=lang).text
        faq[f'answer_{lang}'] = translator.translate(faq['answer'], dest=lang).text
    return faq

# Function to get FAQs in a specific language, with caching
def get_translated_faqs(lang='en'):
    cached_faqs = cache.get(f'faqs_{lang}')  # Check if data is cached
    if cached_faqs:
        return json.loads(cached_faqs)  # Return cached data if available
    
    faqs = list(db.find({}, {'_id': 0}))  # Get FAQs from database
    formatted_faqs = [
        {
            'question': faq.get(f'question_{lang}', faq['question']),
            'answer': faq.get(f'answer_{lang}', faq['answer'])
        } for faq in faqs
    ]
    
    cache.set(f'faqs_{lang}', json.dumps(formatted_faqs, ensure_ascii=False), ex=3600)  # Store in cache for 1 hour
    return formatted_faqs

# API to fetch FAQs in different languages
@app.route('/api/faqs/', methods=['GET'])
def fetch_faqs():
    language = request.args.get('lang', 'en')  # Get language from request
    return jsonify(get_translated_faqs(language))

# API to add a new FAQ
@app.route('/api/faqs/', methods=['POST'])
def add_faq():
    data = request.json  # Get request data
    if not data or 'question' not in data or 'answer' not in data:
        return jsonify({'error': 'Invalid input data'}), 400  # Error if required fields are missing
    
    new_faq = save_translations({'question': data['question'], 'answer': data['answer']})  # Translate
    db.insert_one(new_faq)  # Save in database
    cache.delete_pattern('faqs_*')  # Clear cache
    return jsonify({'message': 'FAQ added successfully'}), 201

# API to delete an FAQ
@app.route('/api/faqs/<question>', methods=['DELETE'])
def delete_faq(question):
    if db.delete_one({'question': question}).deleted_count > 0:
        cache.delete_pattern('faqs_*')  # Clear cache
        return jsonify({'message': 'FAQ deleted successfully'}), 200
    return jsonify({'error': 'FAQ not found'}), 404  # Error if FAQ not found

# API to update an existing FAQ
@app.route('/api/faqs/<question>', methods=['PUT'])
def update_faq(question):
    data = request.json  # Get request data
    if not data or 'answer' not in data:
        return jsonify({'error': 'Invalid input data'}), 400  # Error if required field is missing
    
    updated_faq = save_translations({'question': question, 'answer': data['answer']})  # Translate
    if db.update_one({'question': question}, {'$set': updated_faq}).matched_count > 0:
        cache.delete_pattern('faqs_*')  # Clear cache
        return jsonify({'message': 'FAQ updated successfully'}), 200
    return jsonify({'error': 'FAQ not found'}), 404  # Error if FAQ not found

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
