# Адресная книга
Практическая задача на курс Языки Сценариев

Рассчитана на работу в Python >= 3.4

Программа собирает данные друзей пользователя
из социальной сети *Вконтакте*
и опционально из социальной сети *Twitter*.


Собранные данные компануются в формат \*.vcf (*vCard*)

### Реализация основного функционала

- Самописная OAuth 1.0 библиотека *Twitter*  [Спецификация API](https://dev.twitter.com/oauth/overview)
- Самописная библиотека *Вконтакте*, основанная на авторизации Implicit Flow  [Спецификация API](https://new.vk.com/dev/auth_mobile)
- Библиотека, реализующая формирование файла \*.vcf в соответствии со спецификацией [vCard](https://tools.ietf.org/html/rfc6350)

### Разбор данных (*.vcf)

- Имя, Фамилия пользователя
- Телефон пользователя
- Фотография пользователя из Социальной Сети ВКонтакте
- Ссылка на страницу пользователя во ВКонтакте
- (Опционально) Ссылка на страницу пользователя в социальной сети ВКонтакте


### Использование дополнительных библиотек:
##### Crypto

- обеспечивает многопользовательский режим
- нет необходимости проходить авторизацию каждый раз при старте приложения, данные подгружаются после ввода мастер-ключа
- токен авторизации становится вечным, появляется возможность поддерживать данные актуальными при запуске в пакетном режиме
