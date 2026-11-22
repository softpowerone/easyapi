## День 1: архитектура

### Схема зависимостей

applications → routing
applications → requests
applications → responses
applications → _types
routing      → _types
requests     → _types
responses    → _types
_types       → (ничего из проекта)

Правило: стрелки только вниз. Верхний модуль (applications) знает обо
всех, нижний (_types) не знает ни о ком.

### Ответ на вопрос

**Можно ли импортировать `Request` в `routing.py`?**
Да. `requests` лежит ниже `routing` в схеме, так что стрелка
`routing → requests` идёт вниз и ничего не ломает. Роутер может
использовать `Request`, потому что `Request` ничего не знает о роутере.

**Можно ли импортировать `Route` в `requests.py`?**
Нет. Это стрелка вверх: `requests → routing`. Если при этом
`routing → requests` тоже есть, получается цикл: Python начинает
импортировать `routing`, тот просит `requests`, а `requests` просит
`routing`, который ещё не дозагрузился. Результат: `ImportError`
(circular import). Кроме того, запрос не должен знать, как устроены
маршруты: он только описывает входящие данные.