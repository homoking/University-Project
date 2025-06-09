const API_URL = 'http://localhost:8080';
let majors = {};

async function loadMajors() {
    try {
        const response = await axios.get(`${API_URL}/departments`);
        majors = response.data;
        // به‌روزرسانی گزینه‌های دانشکده و رشته در DOM
        const departmentFilter = document.getElementById('departmentFilter');
        const majorFilter = document.getElementById('majorFilter');
        const editStudentDepartment = document.getElementById('editStudentDepartment');
        const editStudentMajor = document.getElementById('editStudentMajor');

        if (departmentFilter) {
            departmentFilter.innerHTML = '<option value="">همه دانشکده‌ها</option>';
            Object.keys(majors).forEach(dept => {
                const option = document.createElement('option');
                option.value = dept;
                option.textContent = dept;
                departmentFilter.appendChild(option);
            });
        }

        if (editStudentDepartment) {
            editStudentDepartment.innerHTML = '';
            Object.keys(majors).forEach(dept => {
                const option = document.createElement('option');
                option.value = dept;
                option.textContent = dept;
                editStudentDepartment.appendChild(option);
            });
        }
    } catch (error) {
        showToast('خطا در بارگذاری لیست دانشکده‌ها و رشته‌ها', 'error');
    }
}

// فراخوانی در زمان بارگذاری صفحه
document.addEventListener('DOMContentLoaded', () => {
    loadMajors();
    setupFilterEvents();
    checkLogin();
    setupLogout();
    updateTable();
});




function updateMajorFilterOptions(department = '', selectedMajor = '') {
    const majorSelect = document.getElementById('majorFilter');
    if (!majorSelect) return;

    // فقط در صورت تغییر دانشکده، گزینه‌ها را بازنویسی کنید
    const currentDepartment = majorSelect.dataset.currentDepartment || '';
    if (currentDepartment === department) return;

    majorSelect.innerHTML = '<option value="">همه رشته‌ها</option>';
    if (department && majors[department]) {
        majors[department].forEach(m => {
            const option = document.createElement('option');
            option.value = m;
            option.textContent = m;
            if (m === selectedMajor) option.selected = true;
            majorSelect.appendChild(option);
        });
        majorSelect.disabled = false;
    } else {
        majorSelect.disabled = true;
    }
    majorSelect.dataset.currentDepartment = department; // ذخیره دانشکده فعلی
}

// تابع نمایش toast
function showToast(message, type = 'success', duration = 5000) {
    const toastClass = `custom-toast toast-${type}`;
    const closeBtn = document.createElement('span');
    closeBtn.className = 'toast-close';
    closeBtn.innerHTML = '&times;';
    closeBtn.onclick = (e) => {
        e.stopPropagation();
        toast.hideToast();
    };
    
    const toast = Toastify({
        text: message,
        duration: duration,
        close: false,
        gravity: "top",
        position: "right",
        stopOnFocus: true,
        className: toastClass,
        onClick: function() {
            toast.hideToast();
        },
        avatar: type === 'success' ? 
            'https://img.icons8.com/fluency/48/000000/checked.png' : 
            'https://img.icons8.com/color/48/000000/error--v1.png',
        escapeMarkup: false
    });
    
    toast.showToast();
    const toastElement = document.querySelector('.toastify.on');
    if (toastElement) {
        toastElement.insertBefore(closeBtn, toastElement.firstChild);
    }
    
    return toast;
}

// بررسی وضعیت لاگین
function checkLogin() {
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    if (!isLoggedIn) {
        window.location.href = 'login.html';
    }
}

// مدیریت خروج کاربر
function setupLogout() {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('isLoggedIn');
            window.location.href = 'login.html';
        });
    }
}

async function fetchData(entity, params = {}) {
    try {
        console.log('Fetching data with params:', params); // برای دیباگ
        const response = await axios.get(`${API_URL}/${entity}`, { params });
        return response.data;
    } catch (error) {
        console.error('Error fetching data:', error); // برای دیباگ
        showToast(`خطا در دریافت داده‌ها: ${error.response?.data?.detail || 'خطای ناشناخته'}`, 'error');
        return { items: [], total: 0 };
    }
}





async function updateTable() {
    const entity = document.getElementById('entitySelect').value;
    const department = document.getElementById('departmentFilter').value;
    const major = document.getElementById('majorFilter').value;
    const search = document.getElementById('searchInput').value;

    console.log('Updating table with:', { entity, department, major, search }); // برای دیباگ

    document.getElementById('studentsTable').style.display = entity === 'students' ? 'block' : 'none';
    document.getElementById('teachersTable').style.display = entity === 'teachers' ? 'block' : 'none';
    document.getElementById('coursesTable').style.display = entity === 'courses' ? 'block' : 'none';
    document.getElementById('majorFilterContainer').style.display = entity === 'students' ? 'block' : 'none';


    

    // به‌روزرسانی لیست رشته‌ها بر اساس دانشکده
    const majorSelect = document.getElementById('majorFilter');
    majorSelect.innerHTML = '<option value="">همه رشته‌ها</option>';
    if (department && majors[department]) {
        majors[department].forEach(m => {
            const option = document.createElement('option');
            option.value = m;
            option.textContent = m;
            majorSelect.appendChild(option);
        });
    }

    updateMajorFilterOptions(department, major);

    const params = { limit: 10, offset: 0 };
    if (department) params.department = department;
    if (major && entity === 'students') params.Major = major;
    if (search) params.search = search;

    const data = await fetchData(entity, params);
    const tbody = document.getElementById(`${entity}TableBody`);
    tbody.innerHTML = '';

    if (data.items && data.items.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="${entity === 'students' ? 7 : entity === 'teachers' ? 6 : 6}" class="text-center">موردی یافت نشد</td>`;
        tbody.appendChild(row);
        return;
    }

    if (entity === 'students') {
        data.items.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.STID}</td>
                <td>${item.student_fname}</td>
                <td>${item.student_lname}</td>
                <td>${item.Department}</td>
                <td>${item.Major}</td>
                <td>${item.national_id}</td>
                <td>
                    <button class="action-btn edit-btn" onclick="editStudent('${item.STID}')">ویرایش</button>
                    <button class="action-btn delete-btn" onclick="deleteStudent('${item.STID}')">حذف</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } else if (entity === 'teachers') {
        data.items.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.teacher_id}</td>
                <td>${item.teacher_fname}</td>
                <td>${item.teacher_lname}</td>
                <td>${item.Department}</td>
                <td>${item.national_id}</td>
                <td>
                    <button class="action-btn edit-btn" onclick="editTeacher('${item.teacher_id}')">ویرایش</button>
                    <button class="action-btn delete-btn" onclick="deleteTeacher('${item.teacher_id}')">حذف</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } else if (entity === 'courses') {
        data.items.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.course_name}</td>
                <td>${item.units}</td>
                <td>${item.department}</td>
                <td>${item.teacher_id}</td>
                <td>
                    <button class="action-btn edit-btn" onclick="editCourse(${item.id})">ویرایش</button>
                    <button class="action-btn delete-btn" onclick="deleteCourse(${item.id})">حذف</button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }
}

async function editStudent(stid) {
    try {
        const response = await axios.get(`${API_URL}/students/${stid}`);
        const student = response.data;
        document.getElementById('editStudentSTID').value = student.STID;
        document.getElementById('editStudentFname').value = student.student_fname;
        document.getElementById('editStudentLname').value = student.student_lname;
        document.getElementById('editStudentFather').value = student.father;
        document.getElementById('editStudentNationalId').value = student.national_id;
        document.getElementById('editStudentDepartment').value = student.Department;
        document.getElementById('editStudentBirthDate').value = student.birth_date;
        document.getElementById('editStudentMarried').value = student.Married;
        document.getElementById('editStudentAddress').value = student.Address;
        document.getElementById('editStudentPostalCode').value = student.PostalCode;

        // به‌روزرسانی لیست رشته‌ها
        const majorSelect = document.getElementById('editStudentMajor');
        majorSelect.innerHTML = '<option value="">انتخاب کنید</option>';
        if (student.Department && majors[student.Department]) {
            majors[student.Department].forEach(m => {
                const option = document.createElement('option');
                option.value = m;
                option.textContent = m;
                if (m === student.Major) option.selected = true;
                majorSelect.appendChild(option);
            });
        }

        document.getElementById('editStudentModal').classList.remove('hidden');
    } catch (error) {
        showToast(`خطا در دریافت اطلاعات دانشجو: ${error.response?.data?.detail || 'خطای ناشناخته'}`, 'error');
    }
}

async function saveStudentChanges() {
    const stid = document.getElementById('editStudentSTID').value;
    const data = {
        STID: stid,
        student_fname: document.getElementById('editStudentFname').value,
        student_lname: document.getElementById('editStudentLname').value,
        father: document.getElementById('editStudentFather').value,
        national_id: document.getElementById('editStudentNationalId').value,
        Department: document.getElementById('editStudentDepartment').value,
        Major: document.getElementById('editStudentMajor').value,
        birth_date: document.getElementById('editStudentBirthDate').value,
        Married: document.getElementById('editStudentMarried').value,
        Address: document.getElementById('editStudentAddress').value,
        PostalCode: document.getElementById('editStudentPostalCode').value,
        ids_number: '123456', // مقادیر پیش‌فرض برای فیلدهای اجباری
        ids_letter: 'الف',
        ids_code: '01',
        BornCity: 'تهران',
        HPhone: '02112345678'
    };

    try {
        await axios.put(`${API_URL}/students/${stid}`, data);
        showToast('تغییرات دانشجو با موفقیت ذخیره شد', 'success');
        document.getElementById('editStudentModal').classList.add('hidden');
        updateTable();
    } catch (error) {
        showToast(`خطا در ذخیره تغییرات: ${error.response?.data?.detail || 'خطای ناشناخته'}`, 'error');
    }
}

function cancelStudentEdit() {
    document.getElementById('editStudentModal').classList.add('hidden');
}

async function deleteStudent(stid) {
    if (confirm('آیا از حذف این دانشجو مطمئن هستید؟')) {
        try {
            await axios.delete(`${API_URL}/students/${stid}`);
            showToast('دانشجو با موفقیت حذف شد', 'success');
            updateTable();
        } catch (error) {
            showToast(`خطا در حذف دانشجو: ${error.response?.data?.detail || 'خطای ناشناخته'}`, 'error');
        }
    }
}

async function editTeacher(teacherId) {
    try {
        const response = await axios.get(`${API_URL}/teachers/${teacherId}`);
        const teacher = response.data;
        document.getElementById('editTeacherId').value = teacher.teacher_id;
        document.getElementById('editTeacherFname').value = teacher.teacher_fname;
        document.getElementById('editTeacherLname').value = teacher.teacher_lname;
        document.getElementById('editTeacherNationalId').value = teacher.national_id;
        document.getElementById('editTeacherDepartment').value = teacher.Department;

        document.getElementById('editTeacherModal').classList.remove('hidden');
    } catch (error) {
        showToast(`خطا در دریافت اطلاعات استاد: ${error.response?.data?.detail || 'خطای ناشناخته'}`, 'error');
    }
}

async function saveTeacherChanges() {
    const teacherId = document.getElementById('editTeacherId').value;
    const data = {
        teacher_fname: document.getElementById('editTeacherFname').value,
        teacher_lname: document.getElementById('editTeacherLname').value,
        national_id: document.getElementById('editTeacherNationalId').value,
        Department: document.getElementById('editTeacherDepartment').value,
        father: 'نام پیش‌فرض', // مقادیر پیش‌فرض
        ids_number: '123456',
        ids_letter: 'الف',
        ids_code: '01',
        BornCity: 'تهران',
        Address: 'آدرس پیش‌فرض',
        PostalCode: '1234567890',
        HPhone: '02112345678',
        birth_date: '1370/01/01'
    };

    try {
        await axios.put(`${API_URL}/teachers/${teacherId}`, data);
        showToast('تغییرات استاد با موفقیت ذخیره شد', 'success');
        document.getElementById('editTeacherModal').classList.add('hidden');
        updateTable();
    } catch (error) {
        showToast(`خطا در ذخیره تغییرات: ${error.response?.data?.detail || 'خطای ناشناخته'}`, 'error');
    }
}

function cancelTeacherEdit() {
    document.getElementById('editTeacherModal').classList.add('hidden');
}

async function deleteTeacher(teacherId) {
    if (confirm('آیا از حذف این استاد مطمئن هستید؟')) {
        try {
            await axios.delete(`${API_URL}/teachers/${teacherId}`);
            showToast('استاد با موفقیت حذف شد', 'success');
            updateTable();
        } catch (error) {
            showToast(`خطا در حذف استاد: ${error.response?.data?.detail || 'خطای ناشناخته'}`, 'error');
        }
    }
}

async function editCourse(courseId) {
    try {
        const response = await axios.get(`${API_URL}/courses/${courseId}`);
        const course = response.data;
        document.getElementById('editCourseId').value = course.id;
        document.getElementById('editCourseName').value = course.course_name;
        document.getElementById('editCourseUnits').value = course.units;
        document.getElementById('editCourseDepartment').value = course.department;

        // دریافت لیست اساتید
        const teachers = await fetchData('teachers');
        const teacherSelect = document.getElementById('editCourseTeacherId');
        teacherSelect.innerHTML = '<option value="">انتخاب کنید</option>';
        teachers.items.forEach(t => {
            const option = document.createElement('option');
            option.value = t.teacher_id;
            option.textContent = `${t.teacher_fname} ${t.teacher_lname} (${t.teacher_id})`;
            if (t.teacher_id === course.teacher_id) option.selected = true;
            teacherSelect.appendChild(option);
        });

        document.getElementById('editCourseModal').classList.remove('hidden');
    } catch (error) {
        showToast(`خطا در دریافت اطلاعات درس: ${error.response?.data?.detail || 'خطای ناشناخته'}`, 'error');
    }
}

async function saveCourseChanges() {
    const courseId = document.getElementById('editCourseId').value;
    const data = {
        course_name: document.getElementById('editCourseName').value,
        units: parseInt(document.getElementById('editCourseUnits').value),
        department: document.getElementById('editCourseDepartment').value,
        teacher_id: document.getElementById('editCourseTeacherId').value
    };

    try {
        await axios.put(`${API_URL}/courses/${courseId}`, data);
        showToast('تغییرات درس با موفقیت ذخیره شد', 'success');
        document.getElementById('editCourseModal').classList.add('hidden');
        updateTable();
    } catch (error) {
        showToast(`خطا در ذخیره تغییرات: ${error.response?.data?.detail || 'خطای ناشناخته'}`, 'error');
    }
}

function cancelCourseEdit() {
    document.getElementById('editCourseModal').classList.add('hidden');
}

async function deleteCourse(courseId) {
    if (confirm('آیا از حذف این درس مطمئن هستید؟')) {
        try {
            await axios.delete(`${API_URL}/courses/${courseId}`);
            showToast('درس با موفقیت حذف شد', 'success');
            updateTable();
        } catch (error) {
            showToast(`خطا در حذف درس: ${error.response?.data?.detail || 'خطای ناشناخته'}`, 'error');
        }
    }
}

let chartInstance = null;
async function updateChart() {
    const chartType = document.getElementById('chartType').value;
    const ctx = document.getElementById('statsChart').getContext('2d');

    if (chartInstance) chartInstance.destroy();

    if (!chartType) {
        ctx.canvas.parentNode.style.display = 'none';
        return;
    }

    ctx.canvas.parentNode.style.display = 'block';
    let data, labels, datasets;
    try {
        if (chartType === 'studentsByDepartment') {
            const students = await fetchData('students');
            const departments = ['فنی مهندسی', 'علوم پایه', 'اقتصاد'];
            const counts = departments.map(d => students.items.filter(s => s.Department === d).length);
            labels = departments;
            datasets = [{
                label: 'تعداد دانشجویان',
                data: counts,
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
                hoverOffset: 20
            }];
        } else if (chartType === 'coursesByTeacher') {
            const courses = await fetchData('courses');
            const teachers = await fetchData('teachers');
            labels = teachers.items.map(t => `${t.teacher_fname} ${t.teacher_lname}`);
            const counts = teachers.items.map(t => courses.items.filter(c => c.teacher_id === t.teacher_id).length);
            datasets = [{
                label: 'تعداد دروس',
                data: counts,
                backgroundColor: '#36A2EB',
                borderColor: '#1e40af',
                borderWidth: 1
            }];
        }

        chartInstance = new Chart(ctx, {
            type: chartType === 'studentsByDepartment' ? 'pie' : 'bar',
            data: { labels, datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { font: { family: 'Vazirmatn', size: 14 } } },
                    tooltip: { bodyFont: { family: 'Vazirmatn' }, titleFont: { family: 'Vazirmatn' } }
                },
                scales: chartType === 'coursesByTeacher' ? {
                    y: { beginAtZero: true, ticks: { font: { family: 'Vazirmatn' } } },
                    x: { ticks: { font: { family: 'Vazirmatn' } } }
                } : {}
            }
        });
    } catch (error) {
        showToast(`خطا در بارگذاری نمودار: ${error.response?.data?.detail || 'خطای ناشناخته'}`, 'error');
    }
}

function downloadChart() {
    const canvas = document.getElementById('statsChart');
    if (!chartInstance) {
        showToast('ابتدا یک نمودار انتخاب کنید', 'warning');
        return;
    }
    const link = document.createElement('a');
    link.href = canvas.toDataURL('image/png');
    link.download = 'chart.png';
    link.click();
    showToast('نمودار با موفقیت دانلود شد', 'success');
}

// تابع debounce برای تأخیر در جستجو
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, 300); // کاهش تأخیر به 300 میلی‌ثانیه
    };
}

// تنظیم رویدادهای تغییر برای فیلترها
function setupFilterEvents() {
    const entitySelect = document.getElementById('entitySelect');
    const departmentFilter = document.getElementById('departmentFilter');
    const majorFilter = document.getElementById('majorFilter');
    const searchInput = document.getElementById('searchInput');

    if (entitySelect) {
        entitySelect.addEventListener('change', () => {
            if (majorFilter) majorFilter.value = ''; // بازنشانی فیلتر رشته
            updateTable();
        });
    }

    if (departmentFilter) {
        departmentFilter.addEventListener('change', () => {
            if (majorFilter) majorFilter.value = ''; // بازنشانی فیلتر رشته
            updateTable();
        });
    }

    if (majorFilter) {
        majorFilter.addEventListener('change', updateTable);
    }

    if (searchInput) {
        const debouncedUpdateTable = debounce(updateTable, 300);
        searchInput.addEventListener('input', debouncedUpdateTable);
    }
}

// فراخوانی تنظیم رویدادها
setupFilterEvents();

// مدیریت به‌روزرسانی رشته‌ها بر اساس دانشکده در مودال دانشجو
document.getElementById('editStudentDepartment').addEventListener('change', function() {
    const department = this.value;
    const majorSelect = document.getElementById('editStudentMajor');
    majorSelect.innerHTML = '<option value="">انتخاب کنید</option>';
    if (department && majors[department]) {
        majors[department].forEach(m => {
            const option = document.createElement('option');
            option.value = m;
            option.textContent = m;
            majorSelect.appendChild(option);
        });
    }
});

// بررسی لاگین و تنظیم خروج
checkLogin();
setupLogout();

// بارگذاری اولیه جدول
updateTable();