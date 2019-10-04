# Lispy

Реализация LISP по туториалу http://buildyourownlisp.com/

Возможности языка отражены в [тестах](/test_lispy.py)

## Использование

### Сборка (gcc, mingw32)
```
windows> mingw32-make.exe
unix> make
```

### Запуск REPL
```
windows> lispy.exe
unix> ./lispy
```

### Запуск тестов (только windows)

Установить `Python 3.7`, `virtualenv`

Создать виртуальное окружение Python:

```
windows> virtualenv .venv
```

Активировать виртуальное окружение Python:
```
windows> .venv\Scripts\activate
```

Установить зависистмости:
```
windows> python -r requirements.txt
```

Запустить тесты (`test_lispy.py`):
```
windows> pytest -s -p no:warnings
```

