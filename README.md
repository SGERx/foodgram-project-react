# **Foodgram project**

### _Продуктовый помощник_

Доступен по адресу 51.250.71.172

### Технологии:

Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL, Yandex Cloud, Continuous Integration, Continuous Deployment

# Описание

**«Продуктовый помощник»** - это сайт, на котором пользователи могут _публиковать_ рецепты, добавлять чужие рецепты в _избранное_ и _подписываться_ на публикации других авторов. Сервис **«Список покупок»** позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

#### Что могут делать неавторизованные пользователи
- Создать аккаунт.
- Просматривать рецепты на главной.
- Просматривать отдельные страницы рецептов.
- Просматривать страницы пользователей.
- Фильтровать рецепты по тегам.
#### Что могут делать авторизованные пользователи
- Входить в систему под своим логином и паролем.
- Выходить из системы (разлогиниваться).
- Менять свой пароль.
- Создавать/редактировать/удалять собственные рецепты
- Просматривать рецепты на главной.
- Просматривать страницы пользователей.
- Просматривать отдельные страницы рецептов.
- Фильтровать рецепты по тегам.
- Работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов.
- Работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл с количеством необходимых ингредиентов для рецептов из списка покупок.
- Подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.
#### Что может делать администратор
Администратор обладает всеми правами авторизованного пользователя.
Плюс к этому он может:
- изменять пароль любого пользователя,
- создавать/блокировать/удалять аккаунты пользователей,
- редактировать/удалять любые рецепты,
- добавлять/удалять/редактировать ингредиенты.
- добавлять/удалять/редактировать теги.

Все эти функции реализованы в стандартной админ-панели Django.

#### Запуск проекта в контейнерах

- Клонирование удаленного репозитория
```bash
git clone git@github.com:sgerx/foodgram-project-react.git

- Выполните миграции, соберите статику, создайте суперпользователя
```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py createsuperuser
```
- Стандартная админ-панель Django доступна по адресу [`https://localhost/admin/`](https://localhost/admin/)
- Документация к проекту доступна по адресу [`https://localhost/api/docs/`](`https://localhost/api/docs/`)

