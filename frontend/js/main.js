document.addEventListener('DOMContentLoaded', function() {
    // ===== ИНИЦИАЛИЗАЦИЯ ПЕРЕМЕННЫХ =====
    // Навигационная панель
    const profilePicInput = document.getElementById('profilePicInput');
    const hamburger = document.getElementById('hamburger');
    const navButtons = document.getElementById('navButtons');
    
    // Секция курсов
    const coursePanel = document.getElementById('coursePanel');
    const panelMessage = document.getElementById('panelMessage');
    const coursesContainer = document.getElementById('coursesContainer');
    const userName = document.getElementById('userName');
    const prevArrow = document.getElementById('prevArrow');
    const nextArrow = document.getElementById('nextArrow');
    
    // Секция домашних заданий
    const searchBtn = document.getElementById('search-btn');
    const searchName = document.getElementById('search-name');
    const searchDeadline = document.getElementById('search-deadline');
    const searchCourse = document.getElementById('search-course');
    const resultsTable = document.getElementById('results-table');
    const commentModal = document.getElementById('comment-modal');
    const commentInput = document.getElementById('comment-input');
    const saveCommentBtn = document.getElementById('save-comment');
    const modalClose = document.querySelector('.modal-close');
    const cancelBtn = document.querySelector('.cancel-btn');

    // ===== ДАННЫХ =====
    // Данные курсов
    const coursesData = {
        active: [
            {
                name: "Математика для начинающих",
                subject: "Математика",
                students: 25,
                notifications: 3
            },
            {
                name: "Основы программирования",
                subject: "Информатика",
                students: 18,
                notifications: 5
            },
            {
                name: "Физика: механика",
                subject: "Физика",
                students: 12,
                notifications: 1
            },
            {
                name: "Английский язык: начальный уровень",
                subject: "Иностранные языки",
                students: 20,
                notifications: 2
            },
            {
                name: "История искусств",
                subject: "Искусство",
                students: 15,
                notifications: 0
            },
            {
                name: "Химия: основы",
                subject: "Химия",
                students: 22,
                notifications: 4
            }
        ],
        indev: [
            {
                name: "Продвинутая алгебра",
                subject: "Математика",
                students: 0,
                notifications: 0
            },
            {
                name: "Введение в искусственный интеллект",
                subject: "Информатика",
                students: 0,
                notifications: 0
            },
            {
                name: "Биология клетки",
                subject: "Биология",
                students: 0,
                notifications: 0
            }
        ],
        archive: [
            {
                name: "История математики",
                subject: "Математика",
                students: 30,
                notifications: 0
            },
            {
                name: "Основы компьютерной грамотности",
                subject: "Информатика",
                students: 22,
                notifications: 0
            },
            {
                name: "Экспериментальная физика",
                subject: "Физика",
                students: 15,
                notifications: 0
            },
            {
                name: "Литература XIX века",
                subject: "Литература",
                students: 18,
                notifications: 0
            }
        ]
    };

    let currentCourseType = '';

    // ===== ФУНКЦИИ НАВИГАЦИОННОЙ ПАНЕЛИ =====
    function loadUserData() {
        const savedName = localStorage.getItem('teacherName');
        const savedPhoto = localStorage.getItem('teacherPhoto');
        
        if (savedName) {
            document.getElementById('profileName').textContent = savedName;
        }
        
        if (savedPhoto) {
            document.getElementById('profilePic').src = savedPhoto;
        }
    }

    function saveUserData(name, photo) {
        if (name) {
            localStorage.setItem('teacherName', name);
        }
        if (photo) {
            localStorage.setItem('teacherPhoto', photo);
        }
    }

    // Функция для обновления ФИО (для интеграции с формой регистрации)
    window.updateProfileName = function(newName) {
        document.getElementById('profileName').textContent = newName;
        saveUserData(newName, null);
    };

    // ===== ФУНКЦИИ СЕКЦИИ КУРСОВ =====
    function scrollCourses(distance) {
        coursesContainer.scrollBy({
            left: distance,
            behavior: 'smooth'
        });
    }

    function updateCoursePanel(type, title, courses) {
        currentCourseType = type;
        
        // Обновляем сообщение
        panelMessage.textContent = title;
        
        // Добавляем класс активности
        coursePanel.classList.add('active');
        
        // Удаляем предыдущие классы цвета
        coursePanel.classList.remove('active-courses', 'indev-courses', 'archive-courses');
        
        // Добавляем соответствующий класс цвета
        coursePanel.classList.add(`${type}-courses`);
        
        // Очищаем контейнер курсов
        coursesContainer.innerHTML = '';
        
        // Добавляем курсы в контейнер
        if (courses.length > 0) {
            courses.forEach(course => {
                const courseCard = document.createElement('div');
                courseCard.className = 'course-card';
                
                courseCard.innerHTML = `
                    <div class="course-header">${course.name}</div>
                    <div class="course-details">
                        <div class="course-detail"><strong>Направление:</strong> ${course.subject}</div>
                        <div class="course-detail"><strong>Количество учеников:</strong> ${course.students}</div>
                    </div>
                    ${course.notifications > 0 ? `<div class="course-notifications">${course.notifications}</div>` : ''}
                `;
                
                coursesContainer.appendChild(courseCard);
            });
        } else {
            coursesContainer.innerHTML = '<div class="no-courses">Нет курсов в этой категории</div>';
        }
        
        // Прокручиваем к началу
        coursesContainer.scrollLeft = 0;
    }

    // ===== ФУНКЦИИ СЕКЦИИ ДОМАШНИХ ЗАДАНИЙ =====
    function loadCourses() {
        const courses = [
            { id: 1, name: "Математика для начинающих" },
            { id: 2, name: "Основы программирования" },
            { id: 3, name: "Физика: механика" },
            { id: 4, name: "Английский язык: начальный уровень" }
        ];

        courses.forEach(course => {
            const option = document.createElement('option');
            option.value = course.id;
            option.textContent = course.name;
            searchCourse.appendChild(option);
        });
    }

    function smoothScrollToResults() {
        document.getElementById('results-section').scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }

    function renderTable(data) {
        if (data.length === 0) {
            resultsTable.innerHTML = '<div class="no-results">Ничего не найдено</div>';
        } else {
            resultsTable.innerHTML = `
                <div class="homework-row homework-row-header">
                    <div>ФИО ученика</div>
                    <div>Курс</div>
                    <div>Тип работы</div>
                    <div>Требуемый срок</div>
                    <div>Фактический срок</div>
                    <div>Оценка</div>
                    <div>Комментарий</div>
                </div>
                ${data.map(item => `
                    <div class="homework-row" data-id="${item.id}" data-label="${item.studentName} - ${item.course}">
                        <div>${item.studentName}</div>
                        <div>${item.course}</div>
                        <div>${item.type}</div>
                        <div>${formatDate(item.requiredDate)}</div>
                        <div>${item.actualDate ? formatDate(item.actualDate) : "—"}</div>
                        <div>${item.grade || "—"}</div>
                        <div><button class="comment-btn">💬</button></div>
                    </div>
                `).join('')}
            `;
        }

        resultsTable.classList.remove("hidden");
        resultsTable.classList.add("visible");
    }

    function formatDate(dateString) {
        if (!dateString) return "—";
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU');
    }

    // ===== MOCK-ДАННЫЕ ДЛЯ ТЕСТИРОВАНИЯ =====
    // -------- УДАЛИТЬ ПРИ ДАЛЬНЕЙШИХ ЭТАПАХ -----------
    async function searchHomeworks() {
        const name = searchName.value.trim();
        const deadline = searchDeadline.value;
        const course = searchCourse.value;

        try {
            // Временно используем mock-данные вместо реального API
            const mockData = await getMockHomeworks(name, deadline, course);
            renderTable(mockData);
            smoothScrollToResults();
            
        } catch (error) {
            console.error('Ошибка:', error);
            resultsTable.innerHTML = '<div class="error">Ошибка при загрузке данных</div>';
            resultsTable.classList.remove("hidden");
            resultsTable.classList.add("visible");
        }
    }

    function getMockHomeworks(name, deadline, course) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const allHomeworks = [
                    {
                        id: 1,
                        studentName: "Иванов Алексей",
                        course: "Математика для начинающих",
                        type: "Тест",
                        requiredDate: "2025-01-15",
                        actualDate: "2025-01-14",
                        grade: "5",
                        comment: "Отличная работа!"
                    },
                    {
                        id: 2,
                        studentName: "Петрова Мария",
                        course: "Основы программирования",
                        type: "Проект",
                        requiredDate: "2025-01-20",
                        actualDate: null,
                        grade: null,
                        comment: ""
                    },
                    {
                        id: 3,
                        studentName: "Сидоров Иван",
                        course: "Физика: механика",
                        type: "Лабораторная",
                        requiredDate: "2025-01-10",
                        actualDate: "2025-01-11",
                        grade: "4",
                        comment: "Небольшие ошибки в расчетах"
                    },
                    {
                        id: 4,
                        studentName: "Кузнецова Анна",
                        course: "Английский язык: начальный уровень",
                        type: "Эссе",
                        requiredDate: "2025-01-18",
                        actualDate: "2025-01-17",
                        grade: "5",
                        comment: "Отличный словарный запас"
                    }
                ];

                let filtered = allHomeworks;

                if (name) {
                    filtered = filtered.filter(hw => 
                        hw.studentName.toLowerCase().includes(name.toLowerCase())
                    );
                }

                if (course) {
                    filtered = filtered.filter(hw => 
                        hw.course.toLowerCase().includes(
                            searchCourse.options[searchCourse.selectedIndex].text.toLowerCase()
                        )
                    );
                }

                if (deadline) {
                    filtered = filtered.filter(hw => hw.requiredDate === deadline);
                }

                resolve(filtered);
            }, 500);
        });
    }

    async function saveComment() {
        const id = commentModal.dataset.id;
        const text = commentInput.value.trim();

        if (!text) return;

        try {
            const savedComments = JSON.parse(localStorage.getItem('homeworkComments') || '{}');
            savedComments[id] = text;
            localStorage.setItem('homeworkComments', JSON.stringify(savedComments));

            closeCommentModal();
            alert('Комментарий сохранен!');
            
        } catch (error) {
            console.error('Ошибка при сохранении комментария:', error);
            alert('Ошибка при сохранении комментария');
        }
    }

    function openCommentModal(id) {
        const savedComments = JSON.parse(localStorage.getItem('homeworkComments') || '{}');
        commentInput.value = savedComments[id] || '';
        
        commentModal.dataset.id = id;
        commentModal.classList.add("visible");
        document.body.style.overflow = 'hidden';
    }

    function closeCommentModal() {
        commentModal.classList.remove("visible");
        document.body.style.overflow = '';
    }

    // ===== API ФУНКЦИИ (ЗАКОММЕНТИРОВАНЫ ДЛЯ БУДУЩЕГО ИСПОЛЬЗОВАНИЯ) =====
    /*
    async function searchHomeworksAPI() {
        const name = searchName.value.trim();
        const deadline = searchDeadline.value;
        const course = searchCourse.value;

        try {
            const res = await fetch(`/api/homeworks?name=${name}&deadline=${deadline}&course=${course}`);
            
            if (!res.ok) throw new Error('Ошибка при загрузке данных');
            
            const data = await res.json();
            renderTable(data);
            smoothScrollToResults();
            
        } catch (error) {
            console.error('Ошибка:', error);
            resultsTable.innerHTML = '<div class="error">Ошибка при загрузке данных</div>';
            resultsTable.classList.remove("hidden");
            resultsTable.classList.add("visible");
        }
    }

    async function saveCommentAPI() {
        const id = commentModal.dataset.id;
        const text = commentInput.value.trim();

        if (!text) return;

        try {
            await fetch(`/api/homeworks/${id}/comment`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text })
            });

            closeCommentModal();
            
        } catch (error) {
            console.error('Ошибка при сохранении комментария:', error);
            alert('Ошибка при сохранении комментария');
        }
    }
    */

    // ===== ОБРАБОТЧИКИ СОБЫТИЙ =====
    // Навигационная панель
    if (profilePicInput) {
        profilePicInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const newPhoto = event.target.result;
                    document.getElementById('profilePic').src = newPhoto;
                    saveUserData(null, newPhoto);
                };
                reader.readAsDataURL(file);
            }
        });
    }

    if (hamburger) {
        hamburger.addEventListener('click', function() {
            navButtons.classList.toggle('active');
        });
    }

    // Закрытие меню при клике вне его области
    document.addEventListener('click', function(e) {
        if (navButtons && hamburger) {
            if (!navButtons.contains(e.target) && !hamburger.contains(e.target)) {
                navButtons.classList.remove('active');
            }
        }
    });

    // Секция курсов
    if (document.querySelector('.active-course')) {
        document.querySelector('.active-course').addEventListener('click', function() {
            updateCoursePanel('active', 'Активные курсы', coursesData.active);
        });
        
        document.querySelector('.indev-course').addEventListener('click', function() {
            updateCoursePanel('indev', 'Курсы в разработке', coursesData.indev);
        });
        
        document.querySelector('.archive-course').addEventListener('click', function() {
            updateCoursePanel('archive', 'Архивные курсы', coursesData.archive);
        });
    }

    if (prevArrow && nextArrow) {
        prevArrow.addEventListener('click', function() {
            scrollCourses(-300);
        });
        
        nextArrow.addEventListener('click', function() {
            scrollCourses(300);
        });
    }

    // Секция домашних заданий
    if (searchBtn) {
        searchBtn.addEventListener('click', searchHomeworks);
    }

    // Поиск при нажатии Enter в полях ввода
    if (searchName && searchDeadline && searchCourse) {
        [searchName, searchDeadline, searchCourse].forEach(input => {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') searchHomeworks();
            });
        });
    }

    // Клик по строке таблицы
    if (resultsTable) {
        resultsTable.addEventListener('click', (e) => {
            const row = e.target.closest('.homework-row');
            if (row && !row.classList.contains('homework-row-header') && !e.target.classList.contains('comment-btn')) {
                const id = row.dataset.id;
                window.location.href = `/homework.html?id=${id}`;
            }
        });

        // Клик по кнопке комментария
        resultsTable.addEventListener('click', (e) => {
            if (e.target.classList.contains('comment-btn')) {
                const row = e.target.closest('.homework-row');
                const id = row.dataset.id;
                openCommentModal(id);
                e.stopPropagation();
            }
        });
    }

    // Модальное окно комментариев
    if (modalClose) {
        modalClose.addEventListener('click', closeCommentModal);
    }
    
    if (cancelBtn) {
        cancelBtn.addEventListener('click', closeCommentModal);
    }
    
    if (saveCommentBtn) {
        saveCommentBtn.addEventListener('click', saveComment);
    }

    if (commentModal) {
        commentModal.addEventListener('click', (e) => {
            if (e.target === commentModal) {
                closeCommentModal();
            }
        });
    }

    // ===== ИНИЦИАЛИЗАЦИЯ =====
    loadUserData();
    
    if (userName) {
        const savedName = localStorage.getItem('teacherName');
        if (savedName) {
            userName.textContent = savedName;
        }
    }
    
    if (searchCourse) {
        loadCourses();
    }
});