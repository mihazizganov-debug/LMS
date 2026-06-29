# LMS (Learning Management System)

API для онлайн-обучения на Django REST Framework.

## Функционал

- ✅ Управление пользователями (кастомная модель User)
- ✅ CRUD для курсов (ViewSet) и уроков (Generic)
- ✅ JWT-авторизация (регистрация, получение токена)
- ✅ Права доступа: владелец может редактировать свои объекты
- ✅ Группа "Модератор" (может редактировать любые объекты, но не создавать/удалять)
- ✅ Подсчёт количества уроков в курсе (`lessons_count`)
- ✅ Вывод списка уроков внутри курса
- ✅ Модель платежей (оплата курсов и уроков)
- ✅ Фильтрация и сортировка платежей
- ✅ Админ-панель для управления данными
- ✅ Валидация ссылок (только YouTube)    (новое)
- ✅ Модель подписки на обновления курса     (новое)
- ✅ Признак подписки (`is_subscribed`) в списке курсов    (новое)
- ✅ Пагинация для курсов и уроков (по 10 на страницу)    (новое)
- ✅ Переменные окружения (.env)     
- ✅ Подключение PostgreSQL
- ✅ Полное тестирование (CRUD уроков + подписки)
- 
## Технологии

- Python 3.13
- Django 6.0.6
- Django REST Framework 3.17.1
- django-filter
- JWT (SimpleJWT)
- PostgreSQL (с поддержкой SQLite для разработки)
- Pillow (для работы с изображениями)
- python-dotenv (для переменных окружения)

## Эндпоинты API

### Аутентификация

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/users/create/` | Регистрация пользователя |
| POST | `/api/token/` | Получение access/refresh токенов |
| POST | `/api/token/refresh/` | Обновление access-токена |

### Пользователи

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/users/` | Список пользователей (только авторизованные) |
| GET | `/api/users/{id}/` | Детали пользователя |
| PUT/PATCH | `/api/users/{id}/` | Обновить пользователя (только свой профиль) |
| DELETE | `/api/users/{id}/` | Удалить пользователя |

### Курсы и уроки

| Метод | URL | Описание      |
|-------|-----|---------------|
| GET | `/api/courses/` | Список курсов |
| POST | `/api/courses/` | Создать курс  |
| GET | `/api/courses/{id}/` | Детали курса (с уроками и количеством)  |
| PUT/PATCH | `/api/courses/{id}/` | Обновить курс |
| DELETE | `/api/courses/{id}/` | Удалить курс  |
| GET | `/api/lessons/` | Список уроков |
| POST | `/api/lessons/` | Создать урок  |
| GET | `/api/lessons/{id}/` | Детали урока  |
| PUT/PATCH | `/api/lessons/{id}/` | Обновить урок |
| DELETE | `/api/lessons/{id}/` | Удалить урок  |

### Подписки                           (новое)

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/users/subscriptions/` | Добавить/удалить подписку на курс |

### Платежи

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/users/payments/` | Список платежей |
| GET | `/api/users/payments/?course=1` | Фильтр по курсу |
| GET | `/api/users/payments/?lesson=1` | Фильтр по уроку |
| GET | `/api/users/payments/?payment_method=transfer` | Фильтр по способу оплаты |
| GET | `/api/users/payments/?ordering=payment_date` | Сортировка по дате (по возрастанию) |
| GET | `/api/users/payments/?ordering=-payment_date` | Сортировка по дате (по убыванию) |

## Права доступа

| Роль | Создание | Просмотр | Редактирование | Удаление |
|------|----------|----------|----------------|----------|
| **Неавторизованный** | ❌ | ❌ | ❌ | ❌ |
| **Пользователь** | ✅ (свои) | ✅ (свои) | ✅ (свои) | ✅ (свои) |
| **Модератор** | ❌ | ✅ (все) | ✅ (все) | ❌ |
| **Администратор** | ✅ | ✅ | ✅ | ✅ |

## Структура проекта
```
lms/                                        # Корень проекта
│
├── config/                                 # Настройки проекта
│ ├── init.py
│ ├── settings.py                           # Конфигурация Django (INSTALLED_APPS, DRF, база данных)
│ ├── urls.py                               # Главные маршруты (подключение API и админки)
│ ├── asgi.py                               # ASGI конфигурация
│ └── wsgi.py                               # WSGI конфигурация
│
├── lms/                                    # Приложение LMS (курсы и уроки)
│ ├── migrations/                           # Миграции базы данных
│ │ └── _init_.py
│ ├── init.py
│ ├── admin.py                              # Регистрация моделей Course и Lesson в админке
│ ├── apps.py                               # Конфигурация приложения
│ ├── models.py                             # Модели: Course, Lesson (связь один-ко-многим)
│ ├── paginators.py                         # Пагинация             (новое)
│ ├── serializers.py                        # Сериализаторы для API (CourseSerializer, LessonSerializer)
│ ├── tests.py                              # Тесты                  (новое)
│ ├── urls.py                               # Маршруты приложения (courses/, lessons/)
│ ├── validators.py                         # Валидатор ссылок       (новое)
│ └── views.py                              # Контроллеры: CourseViewSet (ViewSet), LessonListCreateView и LessonRetrieveUpdateDestroyView (Generic)
│
├── users/                                  # Приложение пользователей
│ ├── migrations/                           # Миграции пользователей
│ │ └── _init_.py
│ ├── fixtures/                             # Фикстуры для платежей 
│ │ ├── groups.json                         # Группа "Модератор" 
│ │ └── payments.json                       # Платежи для тестов
│ ├── init.py
│ ├── admin.py                              # Регистрация модели User в админке (кастомный UserAdmin)
│ ├── apps.py                               # Конфигурация приложения
│ ├── models.py                             # User, Payment, Subscription    (новое)
│ ├── permissions.py                        # (IsModerator, IsOwner) 
│ ├── serializers.py                        # PaymentSerializer (сериализатор платежей)
│ ├── urls.py                               # Маршруты платежей (/payments/)
│ ├── tests.py                              # Тесты (пустой)
│ └── views.py                              # PaymentListView (фильтрация, сортировка)
│
├── media/                                  # Загруженные изображения (аватары, превью курсов и уроков)
├── static/                                 # Статические файлы (CSS, JS, изображения фона)
├── venv/                                   # Виртуальное окружение (не в git)
├── .env                                    # Переменные окружения (не в git)
├── .env.example                            # Шаблон переменных окружения
├── .gitignore                              # Игнорируемые файлы (venv, pycache, db.sqlite3, .env)
├── .env                                    # Файл переменных окружения        (новое)
├── .env.example                            # Шаблон переменных окружения     (новове)
├── LICENSE                                 # Лицензия MIT
├── manage.py                               # Управляющий скрипт Django
├── README.md                               # Описание проекта
└── requirements.txt                        # Зависимости (включая django-filter)
```

## Модели данных

### User (пользователь) — приложение `users`

| Поле | Тип | Описание |
|------|-----|----------|
| email | EmailField | Уникальный email (используется как логин) |
| phone | CharField (35) | Номер телефона |
| city | CharField (100) | Город |
| avatar | ImageField | Аватарка |
| is_active | BooleanField | Активен ли пользователь |
| is_staff | BooleanField | Доступ в админку |
| is_superuser | BooleanField | Суперпользователь |
| groups | ManyToManyField | Группы пользователя (PermissionsMixin) |
| user_permissions | ManyToManyField | Права пользователя (PermissionsMixin) |

### Course (курс) — приложение `lms`

| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField (200) | Название курса |
| preview | ImageField | Превью |
| description | TextField | Описание |

### Lesson (урок) — приложение `lms`

| Поле | Тип | Описание |
|------|-----|----------|
| name | CharField (200) | Название урока |
| description | TextField | Описание |
| preview | ImageField | Превью |
| video_url | URLField | Ссылка на видео (только YouTube) |
| course | ForeignKey | Связь с курсом |

### Subscription (подписка) — приложение `users`              (новое)

| Поле | Тип | Описание |
|------|-----|----------|
| user | ForeignKey | Пользователь |
| course | ForeignKey | Курс |
| created_at | DateTimeField | Дата подписки |

### Payment (платеж) — приложение `users`

| Поле | Тип | Описание |
|------|-----|----------|
| user | ForeignKey | Пользователь |
| payment_date | DateTimeField | Дата оплаты |
| course | ForeignKey | Оплаченный курс |
| lesson | ForeignKey | Оплаченный урок |
| amount | DecimalField | Сумма |
| payment_method | CharField | Наличные / Перевод |


## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/mihazizganov-debug/lms.git
cd lms

2.Создать и активировать виртуальное окружение
python -m venv venv
venv\Scripts\activate

3.Установить зависимости
pip install -r requirements.txt

4.Применить миграции
python manage.py migrate

5. Загрузить фикстуры
python manage.py loaddata users/fixtures/groups.json
python manage.py loaddata users/fixtures/payments.json

6. Создать суперпользователя
python manage.py createsuperuser
Email: admin@example.com

Password: admin1234

7. Запустить сервер
python manage.py runserver


8. Открыть в браузере
Страница	URL
Корень API	http://127.0.0.1:8000/api/
Список курсов	http://127.0.0.1:8000/api/courses/
Список уроков	http://127.0.0.1:8000/api/lessons/
Админ-панель	http://127.0.0.1:8000/admin/

9. Проверка через Postman
Регистрация:
POST /api/users/create/
{
    "email": "test@example.com",
    "password": "test1234"
}


Получение токена:
POST /api/token/
{
    "email": "test@example.com",
    "password": "test1234"
}


Создание курса (с токеном):
POST /api/courses/
Authorization: Bearer <access-token>
{
    "name": "Мой курс",
    "description": "Описание"
}


Редактирование чужого курса → 403 Forbidden
PUT /api/courses/1/
Authorization: Bearer <access-token-другого-пользователя>


Подписка на курс                (новое)
POST /api/users/subscriptions/
Authorization: Bearer <access-token>
{
    "course": 1
}
→ {"message": "Подписка добавлена"}


Удалить подписку (повторный запрос):     (новое)
POST /api/users/subscriptions/
Authorization: Bearer <access-token>
{
    "course": 1
}
→ {"message": "Подписка удалена"}

 
Проверка is_subscribed                    (новое)
GET /api/courses/
Authorization: Bearer <access-token>

В ответе у каждого курса будет поле is_subscribed: true/false.


Валидация ссылок                               (новое)
Попробуй создать урок с невалидной ссылкой:
POST /api/lessons/
Authorization: Bearer <access-token>
{
    "video_url": "https://vk.com/video"
}
→ 400 Bad Request


Пагинация                               (новое)
GET /api/courses/?page=2
GET /api/courses/?page_size=5

 
Запуск тестов                  (новое)
python manage.py test lms.tests

→ OK


**Проверка модератора:**
1. Назначь пользователя модератором через админку
2. Попробуй создать курс → 403 Forbidden
3. Попробуй отредактировать любой курс → 200 OK
4. Попробуй удалить курс → 403 Forbidden

Лицензия
MIT License

Автор
Михаил Зизганов
