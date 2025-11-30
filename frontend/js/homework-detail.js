document.addEventListener('DOMContentLoaded', function() {
    // Получаем ID домашнего задания из URL
    const urlParams = new URLSearchParams(window.location.search);
    const homeworkId = urlParams.get('id');
    
    // Элементы DOM
    const gradeBtn = document.getElementById('gradeBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const submitGradeBtn = document.getElementById('submitGrade');
    const saveDraftBtn = document.getElementById('saveDraft');
    const requestRevisionBtn = document.getElementById('requestRevision');
    const quickCommentBtns = document.querySelectorAll('.quick-comment-btn');
    const teacherComment = document.getElementById('teacherComment');

    // Загрузка данных домашнего задания
    function loadHomeworkData() {
        // В реальном приложении здесь будет запрос к API
        // Сейчас используем mock-данные
        const homeworkData = {
            id: homeworkId,
            studentName: "Иванов Алексей",
            studentGroup: "МАТ-21-1",
            studentEmail: "alexey.ivanov@edu.ru",
            studentPhone: "+7 (900) 123-45-67",
            courseName: "Математика для начинающих",
            workType: "Тест",
            workTopic: "Линейные уравнения",
            maxPoints: 20,
            assignedDate: "10.01.2024",
            dueDate: "15.01.2024",
            submittedDate: "14.01.2024",
            submissionStatus: "Сдано вовремя",
            currentGrade: null,
            currentPoints: null,
            teacherComment: ""
        };

        // Заполняем данные на странице
        document.getElementById('homeworkId').textContent = homeworkId;
        document.getElementById('studentName').textContent = homeworkData.studentName;
        document.getElementById('studentGroup').textContent = homeworkData.studentGroup;
        document.getElementById('studentEmail').textContent = homeworkData.studentEmail;
        document.getElementById('studentPhone').textContent = homeworkData.studentPhone;
        document.getElementById('courseName').textContent = homeworkData.courseName;
        document.getElementById('workType').textContent = homeworkData.workType;
        document.getElementById('workTopic').textContent = homeworkData.workTopic;
        document.getElementById('maxPoints').textContent = `${homeworkData.maxPoints} макс.`;
        document.getElementById('assignedDate').textContent = homeworkData.assignedDate;
        document.getElementById('dueDate').textContent = homeworkData.dueDate;
        document.getElementById('submittedDate').textContent = homeworkData.submittedDate;
        document.getElementById('submissionStatus').textContent = homeworkData.submissionStatus;

        // Если есть предыдущая оценка, заполняем поля
        if (homeworkData.currentGrade) {
            document.getElementById('grade').value = homeworkData.currentGrade;
        }
        if (homeworkData.currentPoints) {
            document.getElementById('points').value = homeworkData.currentPoints;
        }
        if (homeworkData.teacherComment) {
            teacherComment.value = homeworkData.teacherComment;
        }
    }

    // Обработчики событий
    gradeBtn.addEventListener('click', function() {
        // Прокрутка к секции оценки
        document.querySelector('.grading-section').scrollIntoView({ 
            behavior: 'smooth' 
        });
    });

    downloadBtn.addEventListener('click', function() {
        // Имитация скачивания файлов
        alert('Начинается скачивание всех файлов задания...');
        // В реальном приложении здесь будет логика скачивания
    });

    // Быстрые комментарии
    quickCommentBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const comment = this.getAttribute('data-comment');
            if (teacherComment.value) {
                teacherComment.value += '\n' + comment;
            } else {
                teacherComment.value = comment;
            }
        });
    });

    // Сохранение оценки
    submitGradeBtn.addEventListener('click', function() {
        const grade = document.getElementById('grade').value;
        const points = document.getElementById('points').value;
        const comment = teacherComment.value;

        if (!grade) {
            alert('Пожалуйста, выберите оценку');
            return;
        }

        // Сохранение данных (в реальном приложении - запрос к API)
        console.log('Сохранение оценки:', { grade, points, comment });
        
        alert('Оценка успешно сохранена!');
        
        // Обновление статуса на странице
        document.getElementById('statusBadge').textContent = 'Проверено';
        document.getElementById('statusBadge').style.background = 'var(--success-color)';
    });

    // Сохранение черновика
    saveDraftBtn.addEventListener('click', function() {
        const grade = document.getElementById('grade').value;
        const points = document.getElementById('points').value;
        const comment = teacherComment.value;

        // Сохранение черновика
        console.log('Сохранение черновика:', { grade, points, comment });
        alert('Черновик сохранен!');
    });

    // Запрос доработки
    requestRevisionBtn.addEventListener('click', function() {
        const comment = teacherComment.value;
        
        if (!comment) {
            alert('Пожалуйста, укажите комментарий с замечаниями для доработки');
            return;
        }

        if (confirm('Отправить запрос на доработку задания?')) {
            console.log('Запрос доработки:', { comment });
            alert('Запрос на доработку отправлен студенту!');
            
            // Обновление статуса
            document.getElementById('statusBadge').textContent = 'На доработке';
            document.getElementById('statusBadge').style.background = 'var(--sand)';
        }
    });

    // Скачивание отдельных файлов
    document.querySelectorAll('.file-download').forEach(btn => {
        btn.addEventListener('click', function() {
            const fileName = this.closest('.file-item').querySelector('.file-name').textContent;
            alert(`Начинается скачивание файла: ${fileName}`);
        });
    });

    // Инициализация
    loadHomeworkData();
});