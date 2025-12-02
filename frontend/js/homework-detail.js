document.addEventListener('DOMContentLoaded', function() {
    // Элементы DOM
    const gradeBtn = document.getElementById('gradeBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const gradingForm = document.getElementById('gradingForm');
    const requestRevisionBtn = document.getElementById('requestRevisionBtn');
    const quickCommentBtns = document.querySelectorAll('.quick-comment-btn');
    const editGradeBtn = document.getElementById('editGradeBtn');
    
    // Элементы модального окна доработки
    const revisionModal = document.getElementById('revisionModal');
    const submitRevisionBtn = document.getElementById('submitRevision');
    const cancelRevisionBtn = document.getElementById('cancelRevision');
    const revisionComment = document.getElementById('revisionComment');

    // Обработчики событий
    if (gradeBtn) {
        gradeBtn.addEventListener('click', function() {
            // Прокрутка к секции оценки
            document.querySelector('.grading-section').scrollIntoView({ 
                behavior: 'smooth' 
            });
        });
    }

    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            // Скачивание начнется автоматически по ссылке
            console.log('Начинается скачивание архива с работой...');
        });
    }

    // Быстрые комментарии
    if (quickCommentBtns.length > 0) {
        quickCommentBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const comment = this.getAttribute('data-comment');
                const commentField = document.getElementById('comment');
                
                if (commentField) {
                    if (commentField.value) {
                        commentField.value += '\n' + comment;
                    } else {
                        commentField.value = comment;
                    }
                }
            });
        });
    }

    // Обработка формы оценки (если оценка еще не выставлена)
    if (gradingForm) {
        gradingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const gradeValue = formData.get('grade_value');
            const points = parseInt(formData.get('points'));
            const comment = formData.get('comment');
            
            if (!gradeValue) {
                showToast('Пожалуйста, выберите оценку', 'error');
                return;
            }
            
            if (points > MAX_POINTS) {
                showToast(`Баллы не могут превышать ${MAX_POINTS}`, 'error');
                return;
            }
            
            // Отправка данных на сервер
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Оценка успешно сохранена!', 'success');
                    // Обновляем страницу через 1.5 секунды
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                } else {
                    showToast(data.error || 'Ошибка при сохранении оценки', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Ошибка при отправке данных', 'error');
            });
        });
    }

    // Кнопка "Запросить доработку"
    if (requestRevisionBtn) {
        requestRevisionBtn.addEventListener('click', function() {
            if (revisionModal) {
                revisionModal.classList.remove('hidden');
            }
        });
    }

    // Кнопка "Изменить оценку" (если оценка уже выставлена)
    if (editGradeBtn) {
        editGradeBtn.addEventListener('click', function() {
            // В реальном приложении здесь может быть переход к редактированию
            // Пока просто показываем сообщение
            showToast('Функция редактирования оценки будет доступна в следующей версии', 'info');
        });
    }

    // Модальное окно запроса доработки
    if (submitRevisionBtn) {
        submitRevisionBtn.addEventListener('click', function() {
            const comment = revisionComment.value.trim();
            
            if (!comment) {
                showToast('Пожалуйста, укажите комментарий с замечаниями', 'error');
                return;
            }
            
            // Отправка запроса на доработку
            fetch(`/accounts/homework/${HOMEWORK_ID}/request-revision/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'comment': comment
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Запрос на доработку отправлен студенту!', 'success');
                    revisionModal.classList.add('hidden');
                    revisionComment.value = '';
                    
                    // Обновляем страницу через 1.5 секунды
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                } else {
                    showToast(data.error || 'Ошибка при отправке запроса', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Ошибка при отправке данных', 'error');
            });
        });
    }

    if (cancelRevisionBtn) {
        cancelRevisionBtn.addEventListener('click', function() {
            if (revisionModal) {
                revisionModal.classList.add('hidden');
                revisionComment.value = '';
            }
        });
    }

    // Закрытие модального окна при клике вне его
    if (revisionModal) {
        revisionModal.addEventListener('click', function(e) {
            if (e.target === revisionModal) {
                revisionModal.classList.add('hidden');
                revisionComment.value = '';
            }
        });
    }

    // Функция показа сообщений
    function showToast(message, type = 'info') {
        const toast = document.getElementById('messageToast');
        const toastMessage = document.getElementById('toastMessage');
        
        if (!toast || !toastMessage) return;
        
        // Устанавливаем цвет в зависимости от типа
        const colors = {
            'success': '#28a745',
            'error': '#dc3545',
            'info': '#17a2b8',
            'warning': '#ffc107'
        };
        
        toast.style.backgroundColor = colors[type] || colors.info;
        toastMessage.textContent = message;
        toast.classList.remove('hidden');
        
        // Автоматическое скрытие через 3 секунды
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }

    // Скачивание отдельных файлов (если есть на странице)
    document.querySelectorAll('.file-download').forEach(btn => {
        btn.addEventListener('click', function() {
            const fileName = this.closest('.file-item').querySelector('.file-name').textContent;
            console.log(`Скачивание файла: ${fileName}`);
            // Файл скачается автоматически по ссылке
        });
    });
});