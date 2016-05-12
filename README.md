# Адресная книга
Практическая задача на курс Языки Сценариев
Рассчитана на работу в Python 3.4 и выше

### Возможности

Программа собирает данные друзей пользователя из социальных сетей:
- ВКонтакте
- Twitter

Собранные данные компануются в формат *.vcf (vCard)

### Разбор данных (*.vcf)
Используемые поля:
- Fist Name
- Last Name
- Mobile Phone
- Photo

### Использование дополнительных библиотек:
##### Crypto

- обеспечивает многопользовательский режим
- нет необходимости проходить авторизацию каждый раз при старте приложения, данные подгружаются после ввода мастер-ключа
- токен авторизации становится вечным, появляется возможность поддерживать данные актуальными при запуске в пакетном режиме
