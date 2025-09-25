# WebApp API

##  Project Overview
This project is a **Django + Django REST Framework** based web application with user and product management features. It supports both **Token Authentication** and **Basic Authentication** for secure access. Users can create accounts, view and update their own details, and manage products. Products are public for viewing, but only the owner can update or delete them. The backend uses **MySQL** for persistence and **pytest** for testing.

---

## Prerequisites

### System Requirements
- Python 3.11+ (tested with Python 3.13)
- MySQL 8+
- pip (Python package manager)
- Virtualenv (recommended)

### Programming Language & Frameworks
- **Django** 5.x
- **Django REST Framework (DRF)**
- **pytest** for testing

### Library Dependencies
Install these Python libraries manually (instead of requirements.txt):

```bash
pip install Django>=5.2,<6.0
pip install djangorestframework>=3.15,<4.0
pip install djangorestframework-authtoken>=3.15,<4.0
pip install mysqlclient>=2.2,<3.0   # or pip install PyMySQL>=1.1 if preferred
pip install pytest>=8.0
pip install pytest-django>=4.11
pip install pytest-cov>=7.0
```

---

##  Build & Setup Instructions

1. **Clone the repository**
   ```bash
   git clone git@github.com:vandanarangaswamyy/webapp-fork.git
   cd webapp-fork
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies** (listed above).

4. **Configure MySQL** in `settings.py` (or `.env`):
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'webapp_db',
           'USER': 'root',
           'PASSWORD': '<yourpassword>',
           'HOST': '127.0.0.1',
           'PORT': '3306',
       }
   }
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Start the server**
   ```bash
   python manage.py runserver
   ```

---

## API Endpoints

The API strictly enforces HTTP methods per resource:

- **`/healthz`** → supports only `GET`. Used as a health check (returns 200 if the service is healthy).
- **`/v1/user/`** → accepts only `POST` to create a new user.
- **`/v1/user/{user_id}/`** → supports `GET` to fetch user details and `PUT` to update user details (email cannot be changed).
- **`/v1/product/`** → accepts only `POST` to create a product.
- **`/v1/product/{product_id}/`** → supports `GET` (public access to product details), `PUT`, `PATCH`, and `DELETE` (owner only).
- **Other HTTP methods** on these endpoints will return **405 Method Not Allowed**.

Authentication is enforced with **Token** or **Basic Auth**, depending on how you configure your request.

---

## Testing

Tests are written with **pytest** and `pytest-django`.

Run all tests:
```bash
pytest -v
```

Run with coverage:
```bash
pytest -v --cov=api
``` 
---

## Authentication Notes
- **Token Authentication**: send `Authorization: Token <token>` header.
- **Basic Authentication**: send `-u email:password` in curl.
- Both are enabled in this project (`DEFAULT_AUTHENTICATION_CLASSES` includes both).

---
