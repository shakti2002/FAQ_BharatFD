# Multi-Language FAQ API

A Flask-based API that manages Frequently Asked Questions (FAQs) with multilingual support, caching, and an admin panel.

---

## Features
- **CRUD Operations**: Add, retrieve, update, and delete FAQs.
- **Multilingual Support**: Uses Google Translate to provide automatic translations.
- **Admin Panel**: Manage FAQs using Flask-Admin.
- **Redis Caching**: Improves performance by caching FAQ responses.
- **MongoDB Storage**: Stores FAQs in a NoSQL database.
- **CKEditor Integration**: Enables rich text editing for FAQs.

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/shakti2002/FAQ_BharatFD.git
cd multi-lang-faq-api
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory and add the following:
```
SECRET_KEY=your_secret_key
MONGO_URI=mongodb://your_mongo_uri
REDIS_HOST=your_redis_host
REDIS_PORT=your_redis_port
```

---

## Usage

### Run the Application
```bash
python app.py
```
By default, the app will run at: `http://127.0.0.1:5000`

---

## API Endpoints

### Fetch FAQs (Multilingual)
```
GET /api/faqs/?lang=<language_code>
```
**Example:**
```bash
curl -X GET "http://127.0.0.1:5000/api/faqs/?lang=hi"
```

### Add an FAQ
```
POST /api/faqs/
```


### Update an FAQ
```
PUT /api/faqs/<question>
```


### Delete an FAQ
```
DELETE /api/faqs/<question>
```

---

## Admin Panel

### Access Admin Dashboard
Visit `http://127.0.0.1:5000/admin` to manage FAQs through a web interface.

---

## Technologies Used
- **Flask** - Web framework
- **MongoDB** - NoSQL database
- **Redis** - Caching system
- **Google Translate API** - Automatic translation
- **Flask-Admin** - Admin panel
- **Flask-WTF** - Form handling
- **Flask-CKEditor** - Rich text editor


