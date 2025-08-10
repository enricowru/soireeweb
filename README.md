# soireeweb

## 🛠️ Setup Instructions

### 🔧 1. Create and activate a virtual environment

```bash
python -m venv venv
```

**On Windows:**
```bash
.venv\Scripts\Activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

---

### 📦 2. Install dependencies

```bash
pip install -r requirements.txt
```

✅ This installs all required packages listed in `requirements.txt`.

---

### ➕ 3. Add new packages (Optional)

If you need to add a new package:
```bash
pip install <package-name>
pip freeze > requirements.txt
```

---

## 🐘 4. Install and configure PostgreSQL

> Skip if PostgreSQL is already installed.

1. **Install PostgreSQL**  
   Download from [https://www.postgresql.org/download/](https://www.postgresql.org/download/) and follow the installer instructions.

2. **Create a database:**

```sql
CREATE DATABASE soireeweb;
```

3. **Create or use a PostgreSQL user** (e.g., `postgres`) and ensure the password is known for `.env` config.

---

## 🔐 5. Environment Variables Setup

1. Copy the template file:

```bash
cp .env.copy .env        # macOS/Linux
copy .env.copy .env      # Windows
```

2. Edit the `.env` file with your credentials:

```env
# Localhost
LOCAL_HOST=http://127.0.0.1:8000

# Production
PROD_HOST=https://nikescateringservices.com

# PostgreSQL configuration
PG_DB=soireeweb
PG_USER=postgres
PG_PASS=your_postgres_password
PG_HOST=localhost
PG_PORT=5432
```

> ⚠️ Never commit your `.env` file. It is already ignored via `.gitignore`. Use `.env.copy` as a template for others.

---

## 🧩 6. Seed the Admin User

Run this command to create the initial admin:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_admin
```

---

## 🚀 7. Run the Django Development Server

```bash
python manage.py runserver
```

> Visit: http://127.0.0.1:8000

---

## 📝 Notes

- Do **not** commit the `venv/` folder — it is already in `.gitignore`.
- On another machine:
```bash
python -m venv venv
.venv\Scripts\activate  # or source venv/bin/activate
pip install -r requirements.txt
```
