# 📘 Руководство для фронтенд-разработчика

## 🎯 Что это за API?

Это бэкенд для системы аутентификации пользователей. API позволяет:
- Регистрировать новых пользователей
- Входить в систему (логин)
- Получать информацию о текущем пользователе
- Обновлять токены доступа
- Выходить из системы (логаут)

## 🔗 Базовый URL

```
http://localhost:8000  (для разработки)
```

В продакшене URL будет другим - уточните у бэкенд-разработчика.

## 📋 Доступные endpoints

### 1. Проверка работы API

**GET** `/`

Проверяет, что сервер работает.

**Ответ:**
```json
{
  "status": "ok"
}
```

---

### 2. Регистрация пользователя

**POST** `/auth/register`

Создает нового пользователя в системе.

**Тело запроса (JSON):**
```json
{
  "email": "user@example.com",
  "username": "username123",
  "password": "password123"
}
```

**Требования:**
- `email` - валидный email адрес
- `username` - от 3 до 50 символов
- `password` - минимум 6 символов

**Успешный ответ (201):**
```json
{
  "message": "User registered"
}
```

**Ошибки:**
- `400` - Email или username уже используется
- `422` - Невалидные данные (неправильный формат email, короткий пароль и т.д.)

**Пример запроса (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    username: 'username123',
    password: 'password123'
  })
});

const data = await response.json();
```

---

### 3. Вход в систему (Логин)

**POST** `/auth/login`

Входит в систему и получает токены доступа.

**Тело запроса (JSON):**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Успешный ответ (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Ошибки:**
- `401` - Неверный email или пароль
- `422` - Невалидные данные

**⚠️ ВАЖНО:** Сохраните оба токена! 
- `access_token` - используется для доступа к защищенным endpoints (живет недолго, обычно 15-30 минут)
- `refresh_token` - используется для обновления access_token (живет долго, обычно 7-30 дней)

**Пример запроса (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const data = await response.json();

// Сохраните токены в localStorage или в состоянии приложения
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token);
```

---

### 4. Обновление токенов

**POST** `/auth/refresh`

Обновляет access_token и refresh_token. Используйте этот endpoint, когда access_token истек.

**Тело запроса (JSON):**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Успешный ответ (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Ошибки:**
- `401` - Невалидный или истекший refresh_token

**⚠️ ВАЖНО:** После успешного обновления сохраните новые токены! Старый refresh_token больше не будет работать.

**Пример запроса (JavaScript):**
```javascript
const refreshToken = localStorage.getItem('refresh_token');

const response = await fetch('http://localhost:8000/auth/refresh', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    refresh_token: refreshToken
  })
});

if (response.ok) {
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
} else {
  // Токен истек - нужно заново логиниться
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  // Перенаправить на страницу логина
}
```

---

### 5. Выход из системы (Логаут)

**POST** `/auth/logout`

Выходит из системы и отзывает refresh_token.

**Тело запроса (JSON):**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Успешный ответ (200):**
```json
{
  "message": "Logged out"
}
```

**Пример запроса (JavaScript):**
```javascript
const refreshToken = localStorage.getItem('refresh_token');

await fetch('http://localhost:8000/auth/logout', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    refresh_token: refreshToken
  })
});

// Удалите токены из хранилища
localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');
```

---

### 6. Получение информации о текущем пользователе

**GET** `/users/me`

Получает информацию о текущем авторизованном пользователе.

**⚠️ ТРЕБУЕТ АВТОРИЗАЦИЮ:** Нужно отправить access_token в заголовке Authorization.

**Заголовки:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Успешный ответ (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username123"
}
```

**Ошибки:**
- `401` - Не авторизован (нет токена или токен невалидный)

**Пример запроса (JavaScript):**
```javascript
const accessToken = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8000/users/me', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

if (response.status === 401) {
  // Токен истек - попробуйте обновить через /auth/refresh
  // или перенаправить на логин
}

const userData = await response.json();
console.log(userData); // { id: 1, email: "...", username: "..." }
```

---

## 🔐 Как работать с токенами

### Стратегия работы с токенами

1. **При логине** - сохраните оба токена (access_token и refresh_token)
2. **При каждом запросе** - отправляйте access_token в заголовке `Authorization: Bearer <token>`
3. **Если получили 401** - попробуйте обновить токены через `/auth/refresh`
4. **Если refresh тоже не работает** - перенаправьте пользователя на страницу логина

### Пример функции для автоматического обновления токенов

```javascript
async function fetchWithAuth(url, options = {}) {
  let accessToken = localStorage.getItem('access_token');
  
  // Первый запрос с текущим токеном
  let response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    }
  });
  
  // Если токен истек (401), пробуем обновить
  if (response.status === 401) {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      // Нет refresh токена - нужно логиниться заново
      window.location.href = '/login';
      return;
    }
    
    // Пробуем обновить токены
    const refreshResponse = await fetch('http://localhost:8000/auth/refresh', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh_token: refreshToken
      })
    });
    
    if (refreshResponse.ok) {
      const tokenData = await refreshResponse.json();
      localStorage.setItem('access_token', tokenData.access_token);
      localStorage.setItem('refresh_token', tokenData.refresh_token);
      
      // Повторяем исходный запрос с новым токеном
      response = await fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${tokenData.access_token}`,
          'Content-Type': 'application/json',
        }
      });
    } else {
      // Refresh токен тоже не работает - логин заново
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
      return;
    }
  }
  
  return response;
}

// Использование:
const response = await fetchWithAuth('http://localhost:8000/users/me');
const userData = await response.json();
```

---

## 📝 Коды ответов HTTP

- `200` - Успешно
- `201` - Создано (для регистрации)
- `400` - Неверный запрос (например, email уже используется)
- `401` - Не авторизован (нет токена или токен невалидный)
- `422` - Ошибка валидации данных (неправильный формат email, короткий пароль и т.д.)

---

## 🛠️ Пример полного flow работы с API

### 1. Регистрация
```javascript
// Пользователь регистрируется
const registerResponse = await fetch('http://localhost:8000/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    username: 'user123',
    password: 'password123'
  })
});
```

### 2. Логин
```javascript
// Пользователь входит в систему
const loginResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const { access_token, refresh_token } = await loginResponse.json();
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);
```

### 3. Получение данных пользователя
```javascript
// Получаем информацию о пользователе
const meResponse = await fetch('http://localhost:8000/users/me', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});

const userData = await meResponse.json();
console.log(userData); // { id: 1, email: "...", username: "..." }
```

### 4. Логаут
```javascript
// Выходим из системы
await fetch('http://localhost:8000/auth/logout', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    refresh_token: localStorage.getItem('refresh_token')
  })
});

localStorage.removeItem('access_token');
localStorage.removeItem('refresh_token');
```

---

## ⚠️ Важные моменты

1. **CORS настроен** - API разрешает запросы с фронтенда (настроено в бэкенде)
2. **Токены храните безопасно** - не в обычном localStorage для продакшена (лучше httpOnly cookies, но это требует дополнительной настройки)
3. **Access token короткоживущий** - будьте готовы к его обновлению
4. **Refresh token ротируется** - при каждом обновлении выдается новый refresh_token, старый перестает работать
5. **Всегда проверяйте статус ответа** - не все ошибки возвращают JSON

---

## 🧪 Тестирование API

Вы можете протестировать API через:
- **Swagger UI**: `http://localhost:8000/docs` (автоматическая документация FastAPI)
- **Postman** или другой REST клиент
- **curl** из терминала

Пример curl запроса:
```bash
# Логин
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Получение данных пользователя
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## ❓ Вопросы?

Если что-то непонятно или не работает:
1. Проверьте, что бэкенд запущен
2. Проверьте правильность URL
3. Проверьте формат данных в запросах
4. Проверьте заголовки (особенно Authorization для защищенных endpoints)
5. Посмотрите в консоль браузера на ошибки CORS или сети
6. Обратитесь к бэкенд-разработчику

---

**Удачи в разработке! 🚀**

