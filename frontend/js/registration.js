
// Общие функции валидации
function validateFullName(fullName) {
    const regex = /^[A-Za-zА-Яа-яЁё\s-]+$/;
    return regex.test(fullName) && fullName.trim().split(/\s+/).length >= 2;
}

function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function validateUsername(username) {
    const regex = /^[A-Za-z0-9_]+$/;
    return regex.test(username);
}

function validatePhone(phone) {
    // Убираем маску и проверяем, что осталось 11 цифр
    const digits = phone.replace(/\D/g, '');
    return digits.length === 11;
}

// Валидация пароля
function validatePassword(password, fullName, email, username) {
    const errors = [];
    const requirements = {
        length: password.length >= 8,
        latin: /^[A-Za-z0-9!@#$%^&*()_+=-]+$/.test(password),
        notOnlyDigits: !/^\d+$/.test(password),
        notCommon: !isCommonPassword(password),
        notPersonal: !isSimilarToPersonalInfo(password, fullName, email, username)
    };

    return requirements;
}

// Проверка на распространенные пароли
function isCommonPassword(password) {
    const commonPasswords = [
        'password', '12345678', 'qwerty', 'admin', '1234567890',
        '11111111', 'password1', '123123123', 'abc123', 'qwerty123'
    ];
    return commonPasswords.includes(password.toLowerCase());
}

// Проверка на схожесть с личной информацией
function isSimilarToPersonalInfo(password, fullName, email, username) {
    const personalInfo = [
        fullName,
        fullName.split(' ')[0], // имя
        fullName.split(' ')[1], // фамилия
        email.split('@')[0],    // часть email до @
        username
    ].filter(Boolean); // Убираем пустые значения

    return personalInfo.some(info => 
        info && password.toLowerCase().includes(info.toLowerCase())
    );
}

// Обновление отображения требований к паролю
function updatePasswordRequirements(requirements) {
    const reqIds = {
        length: 'req-length',
        latin: 'req-latin',
        notOnlyDigits: 'req-not-only-digits',
        notCommon: 'req-not-common',
        notPersonal: 'req-not-personal'
    };

    for (const [key, isValid] of Object.entries(requirements)) {
        const element = document.getElementById(reqIds[key]);
        if (element) {
            element.className = `requirement ${isValid ? 'valid' : 'invalid'}`;
            element.querySelector('.requirement-icon').textContent = isValid ? '✓' : '✗';
        }
    }
}

// Проверка всей формы
function validateForm() {
    const fullName = document.getElementById('full_name').value;
    const phone = document.getElementById('phone').value;
    const email = document.getElementById('email').value;
    const username = document.getElementById('username').value;
    const password1 = document.getElementById('password1').value;
    const password2 = document.getElementById('password2').value;

    const isFullNameValid = validateFullName(fullName);
    const isPhoneValid = validatePhone(phone);
    const isEmailValid = validateEmail(email);
    const isUsernameValid = validateUsername(username);
    const passwordRequirements = validatePassword(password1, fullName, email, username);
    const isPasswordValid = Object.values(passwordRequirements).every(req => req);
    const isPassword2Valid = password1 === password2 && password1 !== '';

    // Активация/деактивация кнопки отправки
    const submitBtn = document.getElementById('submit-btn');
    const isFormValid = isFullNameValid && isPhoneValid && isEmailValid && 
                        isUsernameValid && isPasswordValid && isPassword2Valid;
    
    submitBtn.disabled = !isFormValid;

    return isFormValid;
}

// Обработчики событий
document.addEventListener('DOMContentLoaded', function() {
    // Маска телефона
    document.getElementById("phone").addEventListener("input", function (e) {
        let x = this.value.replace(/\D/g, "").substring(0, 11);
        let formatted = "+7 ";

        if (x.length > 1) formatted += "(" + x.substring(1, 4);
        if (x.length >= 4) formatted += ") " + x.substring(4, 7);
        if (x.length >= 7) formatted += "-" + x.substring(7, 9);
        if (x.length >= 9) formatted += "-" + x.substring(9, 11);

        this.value = formatted;
        
        // Валидация
        const isValid = validatePhone(this.value);
        this.classList.toggle('error', !isValid);
        this.classList.toggle('success', isValid);
        document.getElementById('phone_error').style.display = isValid ? 'none' : 'block';
        validateForm();
    });

    // Валидация ФИО
    document.getElementById('full_name').addEventListener('input', function() {
        const isValid = validateFullName(this.value);
        this.classList.toggle('error', !isValid);
        this.classList.toggle('success', isValid);
        document.getElementById('full_name_error').style.display = isValid ? 'none' : 'block';
        
        // Перепроверяем пароль на схожесть с ФИО
        const password = document.getElementById('password1').value;
        if (password) {
            const fullName = this.value;
            const email = document.getElementById('email').value;
            const username = document.getElementById('username').value;
            const passwordRequirements = validatePassword(password, fullName, email, username);
            updatePasswordRequirements(passwordRequirements);
        }
        
        validateForm();
    });

    // Валидация email
    document.getElementById('email').addEventListener('input', function() {
        const isValid = validateEmail(this.value);
        this.classList.toggle('error', !isValid);
        this.classList.toggle('success', isValid);
        document.getElementById('email_error').style.display = isValid ? 'none' : 'block';
        
        // Перепроверяем пароль на схожесть с email
        const password = document.getElementById('password1').value;
        if (password) {
            const fullName = document.getElementById('full_name').value;
            const email = this.value;
            const username = document.getElementById('username').value;
            const passwordRequirements = validatePassword(password, fullName, email, username);
            updatePasswordRequirements(passwordRequirements);
        }
        
        validateForm();
    });

    // Валидация логина
    document.getElementById('username').addEventListener('input', function() {
        const isValid = validateUsername(this.value);
        this.classList.toggle('error', !isValid);
        this.classList.toggle('success', isValid);
        document.getElementById('username_error').style.display = isValid ? 'none' : 'block';
        
        // Перепроверяем пароль на схожесть с логином
        const password = document.getElementById('password1').value;
        if (password) {
            const fullName = document.getElementById('full_name').value;
            const email = document.getElementById('email').value;
            const username = this.value;
            const passwordRequirements = validatePassword(password, fullName, email, username);
            updatePasswordRequirements(passwordRequirements);
        }
        
        validateForm();
    });

    // Валидация пароля
    document.getElementById('password1').addEventListener('input', function() {
        const password = this.value;
        const fullName = document.getElementById('full_name').value;
        const email = document.getElementById('email').value;
        const username = document.getElementById('username').value;
        
        const passwordRequirements = validatePassword(password, fullName, email, username);
        const isPasswordValid = Object.values(passwordRequirements).every(req => req);
        
        this.classList.toggle('error', !isPasswordValid);
        this.classList.toggle('success', isPasswordValid);
        
        updatePasswordRequirements(passwordRequirements);
        validateForm();
    });

    // Валидация подтверждения пароля
    document.getElementById('password2').addEventListener('input', function() {
        const password1 = document.getElementById('password1').value;
        const password2 = this.value;
        const isValid = password1 === password2 && password1 !== '';
        
        this.classList.toggle('error', !isValid);
        this.classList.toggle('success', isValid);
        document.getElementById('password2_error').style.display = isValid ? 'none' : 'block';
        validateForm();
    });

    // Обработчик отправки формы
    document.getElementById("registerForm").addEventListener("submit", function (e) {
        if (!validateForm()) {
            e.preventDefault();
            alert("Пожалуйста, исправьте ошибки в форме перед отправкой.");
        } else {
            // Здесь обычно отправка формы на сервер
            e.preventDefault();
            alert("Форма успешно отправлена!");
            // В реальном приложении здесь был бы fetch или XMLHttpRequest
        }
    });

    // Изначально деактивируем кнопку отправки
    document.getElementById('submit-btn').disabled = true;
});