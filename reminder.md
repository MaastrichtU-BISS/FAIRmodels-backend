executed commands:
```
# python manage.py startapp api
# setup initial database
python manage.py migrate
# Put model changes into migration
python manage.py makemigrations api
# check migration with specific ID
python manage.py sqlmigrate api 0001
# Run all migrations (from last migration id)
python manage.py migrate
```

Play with the shell
```
python manage.py shell
```

Create admin user (for /admin interface)
```
python manage.py createsuperuser
```