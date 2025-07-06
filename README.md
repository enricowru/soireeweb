# soireeweb

## Setup Instructions

### 🔧 1. Create and activate a virtual environment

```bash
python -m venv venv
```

On windows:
```bash
.\venv\Scripts\activate

```
On macOS/Linux:
```bash
source venv/bin/activate
```
### 📦 2. Install dependencies

```bash
pip install -r requirements.txt
```
> ✅ This installs all required packages listed in requirements.txt.

### ➕ 3. Add new packages

To install a new Python package and automatically add it to your requirements.txt:

```bash
pip install <package-name>
pip freeze > requirements.txt
```

### 4. Setup environment variables and seeder

Copy the provided .env.copy file to .env:
```bash
cp .env.copy .env        # macOS/Linux
copy .env.copy .env      # Windows
```

Edit the `.env` file and configure the required values like database credentials, secret keys, etc.

⚠️ Never commit your .env file — it is ignored via .gitignore. Use .env.copy as a template for others.

Next is to seed the admin so for you to do that simply run:
```bash
python manage.py admin_seeder
```

### 🚀 5. Run the Django development server

```bash
python manage.py runserver
```
> Visit: http://127.0.0.1:8000

## Notes
- Do not commit the venv/ folder. It is already ignored in .gitignore.

- To regenerate the virtual environment on another machine, just run:

```bash
python -m venv venv
.\venv\Scripts\activate  # or source venv/bin/activate
pip install -r requirements.txt
```