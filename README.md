drons-trip-dashboard

### Требования

Необходимо, чтобы были установлены следующие компоненты:

- `Docker` и `docker-compose`

### Запуск

1. Запуск приложения:
```commandline
make docker-run
```

### Тестирование

- Запуск тестов со всеми необходимыми флагами:
```commandline
make test-docker
```

- Запуск тестов с генерацией отчета о покрытии:
```commandline
make test-cov-docker
```

### Статический анализ

- Запуск линтеров:
```commandline
make lint
```

- Запуск форматирования кода:
```commandline
make format
```

### Дополнительные команды

- Создание новой ревизии:
```commandline
make revision
```
- Открытие базы данных внутри Docker-контейнера:
```commandline
make open-db
```

- Открытие контейнера внутри Docker-контейнера:
```commandline
make open-server
```

- Вывести список всех команд и их описание:
```commandline
make help
```
