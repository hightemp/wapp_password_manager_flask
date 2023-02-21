# wapp_password_manager_flask

![](https://asdertasd.site/counter/wapp_password_manager_flask)

Менеджер паролей на flask.

![](screenshots/2022-12-28_23-11.png)

## Как делается релиз

1. Меняем версию, если требуется

```bash
echo 'v0.3' > VERSION
```

2. Выполняем скрипт релиза

- `pyinst` сборка pyinstaller
- `zipapp` сборка zipapp
- `all` для всех

```bash
./release-code.sh all
```

В результате коммитется текущий код и дается тэг текущей версии.
Создается релиз.
После упаковывается проект и прикрепреляется к релизу.
