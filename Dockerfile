# استفاده از ایمیج رسمی پایتون
FROM python:3.11-slim

# تنظیم دایرکتوری کاری
WORKDIR /app

# کپی فایل‌های مورد نیاز
COPY main.py .
COPY repo.js .
COPY index.html .
COPY login.html .
COPY students.html .
COPY teachers.html .
COPY courses.html .
COPY reports.html .
COPY README.md .

# نصب وابستگی‌های پایتون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نصب Uvicorn برای اجرای سرور FastAPI
RUN pip install uvicorn

# تنظیم پورت که اپلیکیشن روی آن اجرا می‌شود
EXPOSE 8000

# دستور اجرای اپلیکیشن
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]