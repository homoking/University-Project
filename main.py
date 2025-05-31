import random
import re
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, validator
from typing import List, Generic, TypeVar

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
DATABASE_URL = "sqlite:///./university.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    STID = Column(String, unique=True)
    student_fname = Column(String)
    student_lname = Column(String)
    father = Column(String)
    ids_number = Column(String)
    ids_letter = Column(String)
    ids_code = Column(String)
    BornCity = Column(String)
    Address = Column(String)
    PostalCode = Column(String)
    HPhone = Column(String)
    Department = Column(String)
    Major = Column(String)
    Married = Column(String)
    national_id = Column(String, unique=True)
    birth_date = Column(String)

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, unique=True, index=True)
    teacher_fname = Column(String)
    teacher_lname = Column(String)
    father = Column(String)
    ids_number = Column(String)
    ids_letter = Column(String)
    ids_code = Column(String)
    BornCity = Column(String)
    Address = Column(String)
    PostalCode = Column(String)
    HPhone = Column(String)
    Department = Column(String)
    national_id = Column(String, unique=True)
    birth_date = Column(String)

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String)
    units = Column(Integer)
    department = Column(String)
    teacher_id = Column(String, ForeignKey("teachers.teacher_id"))

Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class StudentCreate(BaseModel):
    STID: str
    student_fname: str
    student_lname: str
    father: str
    ids_number: str
    ids_letter: str
    ids_code: str
    BornCity: str
    Address: str
    PostalCode: str
    HPhone: str
    Department: str
    Major: str
    Married: str
    national_id: str
    birth_date: str

    @validator("STID")
    def validate_stid(cls, v):
        if not (v.isdigit() and len(v) == 11 and v[3:9] == "114150"):
            raise ValueError("شماره دانشجویی باید ۱۱ رقم باشد و ارقام چهارم تا نهم باید ۱۱۴۱۵۰ باشد")
        return v

    @validator("student_fname", "student_lname", "father")
    def validate_persian_name(cls, v):
        if not re.match(r'^[\u0600-\u06FF\s]+$', v):
            raise ValueError("نام، نام خانوادگی و نام پدر باید فقط شامل حروف فارسی و فاصله باشد")
        return v

    @validator("birth_date")
    def validate_birth_date(cls, v):
        try:
            year, month, day = map(int, v.split("/"))
            if not (1300 <= year <= 1400 and 1 <= month <= 12 and 1 <= day <= 31):
                raise ValueError("تاریخ تولد باید به فرمت شمسی YYYY/MM/DD باشد (سال: ۱۳۰۰-۱۴۰۰، ماه: ۱-۱۲، روز: ۱-۳۱)")
        except:
            raise ValueError("فرمت تاریخ تولد باید به صورت YYYY/MM/DD باشد")
        return v

    @validator("ids_number")
    def validate_ids_number(cls, v):
        if not (v.isdigit() and len(v) == 6):
            raise ValueError("سریال شناسنامه باید یک عدد ۶ رقمی باشد")
        return v

    @validator("ids_letter")
    def validate_ids_letter(cls, v):
        persian_letters = "الفبپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی"
        if v not in persian_letters:
            raise ValueError("حرف سریال شناسنامه باید یکی از حروف الفبای فارسی باشد")
        return v

    @validator("ids_code")
    def validate_ids_code(cls, v):
        if not (v.isdigit() and len(v) == 2):
            raise ValueError("کد سریال شناسنامه باید یک عدد ۲ رقمی باشد")
        return v

    @validator("BornCity")
    def validate_born_city(cls, v):
        cities = [
            "تهران", "مشهد", "اصفهان", "کرج", "شیراز", "تبریز", "قم", "اهواز", "کرمانشاه",
            "ارومیه", "رشت", "زاهدان", "همدان", "کرمان", "یزد", "اردبیل", "بندرعباس",
            "اراک", "اسلامشهر", "زنجان", "سنندج", "قزوین", "خرم‌آباد", "گرگان",
            "ساری", "بجنورد", "بوشهر", "بیرجند", "ایلام", "شهرکرد", "یاسوج"
        ]
        if v not in cities:
            raise ValueError("شهر محل تولد باید یکی از مراکز استان‌های ایران باشد")
        return v

    @validator("Address")
    def validate_address(cls, v):
        if len(v) > 100:
            raise ValueError("آدرس نباید بیشتر از ۱۰۰ کاراکتر باشد")
        return v

    @validator("PostalCode")
    def validate_postal_code(cls, v):
        if not (v.isdigit() and len(v) == 10):
            raise ValueError("کد پستی باید یک عدد ۱۰ رقمی باشد")
        return v

    @validator("HPhone")
    def validate_hphone(cls, v):
        if not re.match(r'^0\d{2,3}\d{8}$', v):
            raise ValueError("شماره تلفن ثابت باید با فرمت استاندارد ایران باشد (مثال: ۰۲۱۱۲۳۴۵۶۷۸)")
        return v

    @validator("Department")
    def validate_department(cls, v):
        departments = ["فنی مهندسی", "علوم پایه", "اقتصاد"]
        if v not in departments:
            raise ValueError("دانشکده باید یکی از گزینه‌های فنی مهندسی، علوم پایه یا اقتصاد باشد")
        return v

    @validator("Major")
    def validate_major(cls, v, values):
        majors = {
            "فنی مهندسی": [
                "مهندسی کامپیوتر", "مهندسی برق", "مهندسی مکانیک", "مهندسی عمران",
                "مهندسی صنایع", "مهندسی شیمی", "مهندسی مواد", "مهندسی هوافضا",
                "مهندسی نفت", "مهندسی معماری"
            ],
            "علوم پایه": [
                "ریاضی", "فیزیک", "شیمی", "زیست‌شناسی", "زمین‌شناسی",
                "آمار", "علوم کامپیوتر", "بیوشیمی", "میکروبیولوژی", "ژنتیک"
            ],
            "اقتصاد": [
                "اقتصاد", "مدیریت بازرگانی", "حسابداری", "مدیریت مالی",
                "مدیریت صنعتی", "اقتصاد کشاورزی", "اقتصاد بین‌الملل",
                "بانکداری", "بیمه", "مدیریت دولتی"
            ]
        }
        department = values.get("Department")
        if department not in majors or v not in majors[department]:
            raise ValueError("رشته تحصیلی باید با دانشکده انتخاب‌شده مطابقت داشته باشد")
        return v

    @validator("Married")
    def validate_married(cls, v):
        if v not in ["مجرد", "متاهل"]:
            raise ValueError("وضعیت تأهل باید یکی از گزینه‌های مجرد یا متأهل باشد")
        return v

    @validator("national_id")
    def validate_national_id(cls, v):
        if not (v.isdigit() and len(v) == 10):
            raise ValueError("کد ملی باید یک عدد ۱۰ رقمی باشد")
        return v

    class Config:
        validate_assignment = True
        extra = "forbid"
        strict = True

class StudentResponse(StudentCreate):
    class Config:
        orm_mode = True
        validate_assignment = True
        extra = "forbid"
        strict = True

class TeacherCreate(BaseModel):
    teacher_fname: str
    teacher_lname: str
    father: str
    ids_number: str
    ids_letter: str
    ids_code: str
    BornCity: str
    Address: str
    PostalCode: str
    HPhone: str
    Department: str
    national_id: str
    birth_date: str

    @validator("teacher_fname", "teacher_lname", "father")
    def validate_persian_name(cls, v):
        if not re.match(r'^[\u0600-\u06FF\s]+$', v):
            raise ValueError("نام، نام خانوادگی و نام پدر باید فقط شامل حروف فارسی و فاصله باشد")
        return v

    @validator("birth_date")
    def validate_birth_date(cls, v):
        try:
            year, month, day = map(int, v.split("/"))
            if not (1300 <= year <= 1400 and 1 <= month <= 12 and 1 <= day <= 31):
                raise ValueError("تاریخ تولد باید به فرمت شمسی YYYY/MM/DD باشد (سال: ۱۳۰۰-۱۴۰۰، ماه: ۱-۱۲، روز: ۱-۳۱)")
        except:
            raise ValueError("فرمت تاریخ تولد باید به صورت YYYY/MM/DD باشد")
        return v

    @validator("ids_number")
    def validate_ids_number(cls, v):
        if not (v.isdigit() and len(v) == 6):
            raise ValueError("سریال شناسنامه باید یک عدد ۶ رقمی باشد")
        return v

    @validator("ids_letter")
    def validate_ids_letter(cls, v):
        persian_letters = "الفبپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی"
        if v not in persian_letters:
            raise ValueError("حرف سریال شناسنامه باید یکی از حروف الفبای فارسی باشد")
        return v

    @validator("ids_code")
    def validate_ids_code(cls, v):
        if not (v.isdigit() and len(v) == 2):
            raise ValueError("کد سریال شناسنامه باید یک عدد ۲ رقمی باشد")
        return v

    @validator("BornCity")
    def validate_born_city(cls, v):
        cities = [
            "تهران", "مشهد", "اصفهان", "کرج", "شیراز", "تبریز", "قم", "اهواز", "کرمانشاه",
            "ارومیه", "رشت", "زاهدان", "همدان", "کرمان", "یزد", "اردبیل", "بندرعباس",
            "اراک", "اسلامشهر", "زنجان", "سنندج", "قزوین", "خرم‌آباد", "گرگان",
            "ساری", "بجنورد", "بوشهر", "بیرجند", "ایلام", "شهرکرد", "یاسوج"
        ]
        if v not in cities:
            raise ValueError("شهر محل تولد باید یکی از مراکز استان‌های ایران باشد")
        return v

    @validator("PostalCode")
    def validate_postal_code(cls, v):
        if not (v.isdigit() and len(v) == 10):
            raise ValueError("کد پستی باید یک عدد ۱۰ رقمی باشد")
        return v

    @validator("HPhone")
    def validate_hphone(cls, v):
        if not re.match(r'^0\d{2,3}\d{8}$', v):
            raise ValueError("شماره تلفن ثابت باید با فرمت استاندارد ایران باشد (مثال: ۰۲۱۱۲۳۴۵۶۷۸)")
        return v

    @validator("Department")
    def validate_department(cls, v):
        departments = ["فنی مهندسی", "علوم پایه", "اقتصاد"]
        if v not in departments:
            raise ValueError("دانشکده باید یکی از گزینه‌های فنی مهندسی، علوم پایه یا اقتصاد باشد")
        return v

    @validator("national_id")
    def validate_national_id(cls, v):
        if not (v.isdigit() and len(v) == 10):
            raise ValueError("کد ملی باید یک عدد ۱۰ رقمی باشد")
        return v

    class Config:
        validate_assignment = True
        extra = "forbid"
        strict = True

class TeacherResponse(TeacherCreate):
    teacher_id: str

    class Config:
        orm_mode = True
        validate_assignment = True
        extra = "forbid"
        strict = True

class CourseCreate(BaseModel):
    course_name: str
    units: int
    department: str
    teacher_id: str

    @validator("course_name")
    def validate_course_name(cls, v):
        if not re.match(r'^[\u0600-\u06FF\s]+$', v):
            raise ValueError("نام درس باید فقط شامل حروف فارسی و فاصله باشد")
        if len(v.strip()) == 0:
            raise ValueError("نام درس نمی‌تواند خالی باشد")
        return v

    @validator("units")
    def validate_units(cls, v):
        if not (1 <= v <= 4):
            raise ValueError("تعداد واحدهای درس باید بین ۱ تا ۴ باشد")
        return v

    @validator("department")
    def validate_department(cls, v):
        departments = ["فنی مهندسی", "علوم پایه", "اقتصاد"]
        if v not in departments:
            raise ValueError("دانشکده باید یکی از گزینه‌های فنی مهندسی، علوم پایه یا اقتصاد باشد")
        return v

    @validator("teacher_id")
    def validate_teacher_id(cls, v):
        if not (v.isdigit() and len(v) == 6):
            raise ValueError("شناسه استاد باید یک عدد ۶ رقمی باشد")
        return v

    class Config:
        validate_assignment = True
        extra = "forbid"
        strict = True

class CourseResponse(CourseCreate):
    id: int

    class Config:
        orm_mode = True
        validate_assignment = True
        extra = "forbid"
        strict = True

# Pagination Schema
T = TypeVar('T')
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int

    class Config:
        orm_mode = True
        validate_assignment = True
        extra = "forbid"
        strict = True

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helpers
def generate_teacher_id(db: Session):
    while True:
        teacher_id = f"{random.randint(100000, 999999)}"
        if not db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first():
            return teacher_id

# Routes
@app.post("/students", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    print("Received student data:", student.dict())  # برای دیباگ
    # بررسی یکتایی کدملی
    db_student = db.query(Student).filter(Student.national_id == student.national_id).first()
    if db_student:
        raise HTTPException(status_code=400, detail="کدملی قبلاً ثبت شده است")
    # بررسی یکتایی STID
    db_student = db.query(Student).filter(Student.STID == student.STID).first()
    if db_student:
        raise HTTPException(status_code=400, detail="شماره دانشجویی قبلاً ثبت شده است")
    db_student = Student(**student.dict())
    try:
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"خطا در ذخیره دانشجو: {str(e)}")
    return db_student

@app.get("/students", response_model=PaginatedResponse[StudentResponse])
def get_students(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, description="تعداد رکوردها در هر صفحه"),
    offset: int = Query(0, ge=0, description="شروع از شماره رکورد"),
    department: str = Query(None, description="فیلتر بر اساس دانشکده"),
    major: str = Query(None, description="فیلتر بر اساس رشته"),
    search: str = Query(None, description="جستجو بر اساس نام یا کد")
):
    query = db.query(Student)
    if department:
        query = query.filter(Student.Department == department)
    if major:
        query = query.filter(Student.Major == major)
    if search:
        query = query.filter(
            (Student.student_fname.contains(search)) |
            (Student.student_lname.contains(search)) |
            (Student.STID.contains(search)) |
            (Student.national_id.contains(search))
        )
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return {"items": items, "total": total}

@app.get("/students/{stid}", response_model=StudentResponse)
def get_student(stid: str, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.STID == stid).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="دانشجو یافت نشد")
    return db_student

@app.put("/students/{stid}", response_model=StudentResponse)
def update_student(stid: str, student: StudentCreate, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.STID == stid).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="دانشجو یافت نشد")
    # بررسی یکتایی کدملی برای سایر دانشجویان
    existing_student = db.query(Student).filter(Student.national_id == student.national_id, Student.STID != stid).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="کدملی قبلاً ثبت شده است")
    # بررسی یکتایی STID برای سایر دانشجویان
    existing_student = db.query(Student).filter(Student.STID == student.STID, Student.STID != stid).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="شماره دانشجویی قبلاً ثبت شده است")
    for key, value in student.dict().items():
        setattr(db_student, key, value)
    try:
        db.commit()
        db.refresh(db_student)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"خطا در به‌روزرسانی دانشجو: {str(e)}")
    return db_student

@app.delete("/students/{stid}")
def delete_student(stid: str, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.STID == stid).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="دانشجو یافت نشد")
    db.delete(db_student)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"خطا در حذف دانشجو: {str(e)}")
    return {"detail": "دانشجو حذف شد"}

@app.post("/teachers", response_model=TeacherResponse)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    print("Received teacher data:", teacher.dict())  # برای دیباگ
    db_teacher = db.query(Teacher).filter(Teacher.national_id == teacher.national_id).first()
    if db_teacher:
        raise HTTPException(status_code=400, detail="کدملی قبلاً ثبت شده است")
    teacher_id = generate_teacher_id(db)
    db_teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if db_teacher:
        raise HTTPException(status_code=400, detail="شماره استاد قبلاً ثبت شده است")
    db_teacher = Teacher(**teacher.dict(), teacher_id=teacher_id)
    try:
        db.add(db_teacher)
        db.commit()
        db.refresh(db_teacher)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"خطا در ذخیره استاد: {str(e)}")
    return db_teacher

@app.get("/teachers", response_model=PaginatedResponse[TeacherResponse])
def get_teachers(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, description="تعداد رکوردها در هر صفحه"),
    offset: int = Query(0, ge=0, description="شروع از شماره رکورد"),
    department: str = Query(None, description="فیلتر بر اساس دانشکده"),
    search: str = Query(None, description="جستجو بر اساس نام یا کد")
):
    query = db.query(Teacher)
    if department:
        query = query.filter(Teacher.Department == department)
    if search:
        query = query.filter(
            (Teacher.teacher_fname.contains(search)) |
            (Teacher.teacher_lname.contains(search)) |
            (Teacher.teacher_id.contains(search)) |
            (Teacher.national_id.contains(search))
        )
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return {"items": items, "total": total}

@app.get("/teachers/{teacher_id}", response_model=TeacherResponse)
def get_teacher(teacher_id: str, db: Session = Depends(get_db)):
    db_teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="استاد یافت نشد")
    return db_teacher

@app.put("/teachers/{teacher_id}", response_model=TeacherResponse)
def update_teacher(teacher_id: str, teacher: TeacherCreate, db: Session = Depends(get_db)):
    db_teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="استاد یافت نشد")
    existing_teacher = db.query(Teacher).filter(Teacher.national_id == teacher.national_id, Teacher.teacher_id != teacher_id).first()
    if existing_teacher:
        raise HTTPException(status_code=400, detail="کدملی قبلاً ثبت شده است")
    for key, value in teacher.dict().items():
        setattr(db_teacher, key, value)
    try:
        db.commit()
        db.refresh(db_teacher)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"خطا در به‌روزرسانی استاد: {str(e)}")
    return db_teacher

@app.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: str, db: Session = Depends(get_db)):
    db_teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=404, detail="استاد یافت نشد")
    db.delete(db_teacher)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"خطا در حذف استاد: {str(e)}")
    return {"detail": "استاد حذف شد"}

@app.post("/courses", response_model=CourseResponse)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    print("Received course data:", course.dict())  # برای دیباگ
    db_teacher = db.query(Teacher).filter(Teacher.teacher_id == course.teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=400, detail="استاد یافت نشد")
    db_course = Course(**course.dict())
    try:
        db.add(db_course)
        db.commit()
        db.refresh(db_course)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"خطا در ذخیره درس: {str(e)}")
    return db_course

@app.get("/courses", response_model=PaginatedResponse[CourseResponse])
def get_courses(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, description="تعداد رکوردها در هر صفحه"),
    offset: int = Query(0, ge=0, description="شروع از شماره رکورد"),
    department: str = Query(None, description="فیلتر بر اساس دانشکده"),
    search: str = Query(None, description="جستجو بر اساس نام درس یا کد استاد")
):
    query = db.query(Course)
    if department:
        query = query.filter(Course.department == department)
    if search:
        query = query.filter(
            (Course.course_name.contains(search)) |
            (Course.teacher_id.contains(search))
        )
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return {"items": items, "total": total}

@app.get("/courses/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="درس یافت نشد")
    return db_course

@app.put("/courses/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, course: CourseCreate, db: Session = Depends(get_db)):
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="درس یافت نشد")
    db_teacher = db.query(Teacher).filter(Teacher.teacher_id == course.teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=400, detail="استاد یافت نشد")
    for key, value in course.dict().items():
        setattr(db_course, key, value)
    try:
        db.commit()
        db.refresh(db_course)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"خطا در به‌روزرسانی درس: {str(e)}")
    return db_course

@app.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="درس یافت نشد")
    db.delete(db_course)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"خطا در حذف درس: {str(e)}")
    return {"detail": "درس حذف شد"}



@app.get("/departments")
def get_departments():
    return {
        "فنی مهندسی": [
            "مهندسی کامپیوتر", "مهندسی برق", "مهندسی مکانیک", "مهندسی عمران",
            "مهندسی صنایع", "مهندسی شیمی", "مهندسی مواد", "مهندسی هوافضا",
            "مهندسی نفت", "مهندسی معماری"
        ],
        "علوم پایه": [
            "ریاضی", "فیزیک", "شیمی", "زیست‌شناسی", "زمین‌شناسی",
            "آمار", "علوم کامپیوتر", "بیوشیمی", "میکروبیولوژی", "ژنتیک"
        ],
        "اقتصاد": [
            "اقتصاد", "مدیریت بازرگانی", "حسابداری", "مدیریت مالی",
            "مدیریت صنعتی", "اقتصاد کشاورزی", "اقتصاد بین‌الملل",
            "بانکداری", "بیمه", "مدیریت دولتی"
        ]
    }