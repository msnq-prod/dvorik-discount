# Frontend Integration Guide

Этот документ описывает REST API и доступные возможности бэкенда, чтобы упростить разработку интерфейса для программы лояльности и внутренних HR-сценариев.

## Общая информация об API
- **Базовый URL:** все конечные точки доступны по префиксу `/api/v1`. Приложение также предоставляет health-check `GET /healthz` без авторизации.【F:src/app/main.py†L1-L11】
- **Аутентификация:** на текущем этапе API не требует авторизации. Исключение — телеграм-вебхуки, где используется HMAC-подпись с секретом `BOT_HMAC_SECRET` в заголовке `X-Signature`. Подпись генерируется функцией `create_hmac_signature`, проверка выполняется в вебхуках.【F:src/app/core/security.py†L7-L27】【F:src/app/api/v1/endpoints/webhooks.py†L1-L33】
- **Формат данных:** все запросы/ответы используют JSON. Все схемы описаны через Pydantic и возвращаются в camelCase, совпадая с названиями полей моделей.
- **Ошибки:** при отсутствии сущности большинство обработчиков возвращают `HTTP 404`, бизнес-ошибки (например, неправильный купон) — `HTTP 400` с текстовым описанием.

## Справочник конечных точек
Ниже сгруппированы доступные ресурсы и поддерживаемые операции. В скобках указаны тела запросов/ответов.

### Акции (Campaigns)
- `POST /campaigns/` — создать кампанию (`CampaignCreate`).
- `GET /campaigns/{id}` — получить кампанию по ID (`Campaign`).
- `GET /campaigns/` — список всех кампаний (`Campaign[]`).
- `PUT /campaigns/{id}` — обновить кампанию (`CampaignUpdate`).
- `DELETE /campaigns/{id}` — удалить кампанию (`Campaign`).
- `POST /campaigns/{id}/activate` — установить статус `active`.
- `POST /campaigns/{id}/deactivate` — установить статус `paused`.

Модели кампаний включают название, временные рамки, каналы, UTM-метки и ссылку на шаблон купона, статус берётся из перечисления `CampaignStatusEnum` (`draft`, `active`, `paused`, `ended`).【F:src/app/api/v1/endpoints/campaigns.py†L20-L173】【F:src/app/schemas/promotions.py†L31-L67】【F:src/app/schemas/enums.py†L29-L36】

### Шаблоны купонов (Coupon Templates)
- `POST /coupon-templates/` — создать шаблон (`CouponTemplateCreate`).
- `GET /coupon-templates/{id}` — получить шаблон (`CouponTemplate`).
- `GET /coupon-templates/` — список шаблонов (`CouponTemplate[]`).
- `PUT /coupon-templates/{id}` — обновить шаблон (`CouponTemplateUpdate`).
- `DELETE /coupon-templates/{id}` — удалить шаблон (`CouponTemplate`).

Шаблон задаёт тип скидки (`percent`, `fixed`, `gift`), порог минимальной покупки, ограничения по выдаче и правила стакабельности, что важно для построения UI конструктора купонов.【F:src/app/api/v1/endpoints/coupon_templates.py†L16-L89】【F:src/app/schemas/promotions.py†L10-L30】【F:src/app/schemas/enums.py†L41-L47】

### Купоны (Coupons)
- `POST /coupons/issue` — выдать купон клиенту по шаблону и кампании (`CouponIssueRequest` → `Coupon`).
- `POST /coupons/redeem` — погасить купон (`CouponRedeemRequest` → `CouponRedeemResponse`).
- `GET /coupons/by-code/{code}` — получить купон по коду (`Coupon`).

Сервис выдачи генерирует уникальные коды и фиксирует событие `coupon_issued`, а погашение проверяет статус, срок действия, рассчитывает скидку и обновляет уровень клиента, создавая событие `coupon_redeemed`. Эти процессы критичны для фронта кассиров и клиентского кабинета.【F:src/app/api/v1/endpoints/coupons.py†L20-L78】【F:src/app/services/coupons.py†L26-L74】【F:src/app/services/redemption.py†L27-L106】【F:src/app/schemas/promotions.py†L69-L118】

### Клиенты (Clients)
- `POST /clients/` — регистрация клиента (`ClientCreate`).
- `GET /clients/{id}` — получить клиента (`Client`).
- `PUT /clients/{id}` — обновить клиента (`ClientUpdate`).
- `DELETE /clients/{id}` — удалить клиента (`Client`).
- `GET /clients/by-tg-id/{tgId}` — поиск по Telegram ID (`Client`).
- `GET /clients/{id}/coupons` — активные купоны клиента (`Coupon[]`).

Поля клиента включают персональные данные, идентификатор программы лояльности, текущий уровень, теги и статусы подписок — всё это можно визуализировать в карточке клиента. Уровни с порогами и перками задаются отдельно (см. ниже).【F:src/app/api/v1/endpoints/clients.py†L15-L84】【F:src/app/schemas/loyalty.py†L9-L47】【F:src/app/schemas/promotions.py†L118-L147】

### Уровни лояльности (Levels)
- `POST /levels/` — создать уровень (`LevelCreate`).
- `GET /levels/{id}` — получить уровень (`Level`).
- `GET /levels/` — список уровней (`Level[]`).
- `PUT /levels/{id}` — обновить уровень (`LevelUpdate`).
- `DELETE /levels/{id}` — удалить уровень (`Level`).

Уровень состоит из названия, порога по сумме покупок, порядка отображения и набора перков. Сервис также отвечает за перерасчёт уровней после покупок или погашений купонов, что полезно для отображения прогресса клиента.【F:src/app/api/v1/endpoints/levels.py†L13-L83】【F:src/app/services/loyalty.py†L8-L43】

### Покупки (Purchases)
- `POST /purchases/` — зафиксировать покупку (`PurchaseCreate`).

При записи покупки сервис увеличивает сумму трат клиента, создаёт событие `purchase_recorded` и пересчитывает уровень. Ошибки (например, не найден клиент) возвращаются как `400 Bad Request`. Этот endpoint нужен для фронта кассиров или админки для ручного ввода чеков.【F:src/app/api/v1/endpoints/purchases.py†L20-L34】【F:src/app/services/purchases.py†L20-L47】【F:src/app/schemas/purchases.py†L7-L10】

### Сотрудники (Employees)
- `POST /employees/` — создать сотрудника (`EmployeeCreate`).
- `GET /employees/{id}` — получить сотрудника (`Employee`).
- `PUT /employees/{id}` — обновить сотрудника (`EmployeeUpdate`).
- `DELETE /employees/{id}` — удалить сотрудника (`Employee`).
- `GET /employees/by-tg-id/{tgId}` — найти сотрудника по Telegram ID (`Employee`).
- `GET /employees/{id}/shifts` — получить смены сотрудника (`Shift[]`).

Создание/изменение/удаление сопровождается аудитом, что важно для журналирования действий HR. Модель сотрудника хранит роль (кассир, админ и т.д.), ставку и статус активности.【F:src/app/api/v1/endpoints/employees.py†L18-L94】【F:src/app/schemas/hr.py†L7-L33】【F:src/app/schemas/enums.py†L19-L27】

### Смены (Shifts)
- `POST /shifts/` — создать смену (`ShiftCreate`).
- `GET /shifts/{id}` — получить смену (`Shift`).
- `GET /shifts/` — список смен (`Shift[]`).
- `PUT /shifts/{id}` — обновить смену (`ShiftUpdate`).
- `DELETE /shifts/{id}` — удалить смену (`Shift`).

Сервис смен предоставляет CRUD и интегрируется с аудитом, позволяя строить UI календаря смен или расписания сотрудников.【F:src/app/api/v1/endpoints/shifts.py†L13-L83】【F:src/app/services/shifts.py†L8-L27】【F:src/app/schemas/hr.py†L21-L33】

### Расчёт зарплаты (Payrolls)
- `POST /payrolls/calculate?employee_id=&month=` — расчёт payroll для сотрудника за месяц (возвращает `Payroll`).
- `GET /payrolls/` — список расчётных листов (`Payroll[]`).

При расчёте учитываются смены в выбранном месяце, считается валовая сумма, налоги (заглушка 13%) и чистая выплата, далее действие логируется. Можно строить UI для расчётных листков и истории выплат.【F:src/app/api/v1/endpoints/payrolls.py†L19-L59】【F:src/app/services/payroll.py†L11-L52】【F:src/app/schemas/hr.py†L35-L53】

### Рассылки (Broadcasts)
- `POST /broadcasts/` — создать рассылку (`BroadcastCreate`).
- `GET /broadcasts/{id}` — получить рассылку (`Broadcast`).
- `GET /broadcasts/` — список рассылок (`Broadcast[]`).
- `PUT /broadcasts/{id}` — обновить рассылку (`BroadcastUpdate`).
- `DELETE /broadcasts/{id}` — удалить рассылку (`Broadcast`).

При наличии `schedule_at` рассылка автоматически планируется в Celery-задачу. В ответах присутствуют счётчики отправленных/ошибочных сообщений, что позволяет строить интерфейс мониторинга рассылок.【F:src/app/api/v1/endpoints/broadcasts.py†L11-L67】【F:src/app/services/broadcasts.py†L8-L33】【F:src/app/schemas/broadcasts.py†L9-L26】

### Дашборд (Dashboard)
- `GET /dashboard/?start_date=&end_date=` — агрегированные метрики: количество выданных/погашенных купонов, число покупок и оборот за период (`DashboardData`). При отсутствии дат используется текущий день.【F:src/app/api/v1/endpoints/dashboard.py†L16-L34】【F:src/app/services/dashboard.py†L11-L44】【F:src/app/schemas/dashboard.py†L1-L9】

### Аудит и события
- `GET /audit-logs/?skip=&limit=` — список аудиторских событий (`AuditLog[]`).
- `GET /events/?skip=&limit=` — поток бизнес-событий (`Event[]`).

Оба репозитория поддерживают пагинацию через `skip/limit`, что можно использовать в UI журналов действий и триггеров интеграций.【F:src/app/api/v1/endpoints/audit_logs.py†L12-L30】【F:src/app/api/v1/endpoints/events.py†L11-L27】【F:src/app/schemas/events.py†L8-L35】

### Вебхуки телеграм-ботов
- `POST /webhooks/client` — обновления от клиентского бота.
- `POST /webhooks/worker` — обновления от бота сотрудников.

Запросы должны включать HMAC-подпись в `X-Signature`; при проверке тело запроса прокидывается в `aiogram` диспетчеры. Для фронта важно обеспечить настройку вебхуков и мониторинг статуса ботов.【F:src/app/api/v1/endpoints/webhooks.py†L7-L33】【F:src/bots/bot.py†L6-L19】

## Ключевые возможности бэкенда
Ниже перечислены готовые сервисы и инфраструктурные компоненты, которые можно задействовать во фронтенде или при интеграциях.

- **Управление акциями и купонами:** сервисы создают кампании, генерируют коды на основе шаблонов и логируют события в журнал (`coupon_issued`, `coupon_redeemed`). Купон можно активировать/деактивировать, проверяется срок действия и принадлежность клиенту, что важно для интерфейсов маркетинга и кассиров.【F:src/app/services/campaigns.py†L12-L45】【F:src/app/services/coupons.py†L26-L74】【F:src/app/services/redemption.py†L27-L106】
- **Лояльность и покупки:** перерасчёт уровней происходит при покупках и погашениях, уровни сортируются по порогу и обновляют клиента. Это позволяет отображать прогресс и перки без дополнительной логики на фронте.【F:src/app/services/loyalty.py†L8-L26】【F:src/app/services/purchases.py†L20-L47】
- **HR-модуль:** хранит сотрудников, смены, расчёты зарплат. Payroll-сервис рассчитывает зарплату по сменам за месяц, смены можно планировать и просматривать, а действия логируются в аудит — пригодно для админки HR.【F:src/app/api/v1/endpoints/employees.py†L18-L94】【F:src/app/services/shifts.py†L8-L27】【F:src/app/services/payroll.py†L11-L52】
- **Рассылки и сегментация:** Celery-задача `send_broadcast` берёт аудиторию по динамическим фильтрам, отправляет сообщения через клиентского бота и считает статистику доставки. Фильтры строятся как дерево `and/or` с операторами (`==`, `in`, `contains` и т.д.), что можно обернуть в визуальный конструктор сегментов на фронте.【F:src/app/services/broadcasts.py†L8-L33】【F:src/app/workers/broadcast.py†L1-L43】【F:src/app/services/segmentation.py†L1-L37】
- **Аудит и события:** отдельные сервисы записывают действия админов и бизнес-события в БД для отображения журналов, триггеров или аналитики.【F:src/app/services/events.py†L7-L20】
- **Телеграм-боты:** существует два `aiogram`-бота. Клиентский бот умеет регистрировать клиентов, показывать уровень/купоны и автоматически выдаёт купон при старте с параметром кампании. Рабочий бот помогает кассиру погашать купоны, фиксировать покупки и смотреть расписание. Это готовые сценарии, которые можно перенести в веб-интерфейс или использовать как подсказку для UX.【F:src/bots/client_bot/__main__.py†L8-L131】【F:src/bots/worker_bot/__main__.py†L8-L116】
- **Инфраструктура:** docker-compose разворачивает API, Celery worker/beat, Postgres и Redis, обеспечивая фоновые задачи и хранилище. Это облегчает локальный стенд для фронта и интеграций.【F:docker-compose.yml†L3-L72】【F:src/app/celery_app.py†L1-L12】

## Советы для интеграции фронтенда
- Используйте журналы аудита и событий для построения административных разделов с историей действий и триггеров.
- При работе с купонами и покупками отображайте текстовые сообщения об ошибках из `detail` тела ответа — бэкенд формирует человеко-понятные сообщения.
- Для UI конструктора сегментов предоставьте пользователю выбор операторов, которые поддерживает `SegmentationService`, и продумайте дефолтный фильтр «все клиенты», так как пустой фильтр возвращает пустой список.
- При интеграции с телеграм-ботами убедитесь, что фронтенд-сервис, который выставляет вебхуки, умеет подписывать запросы HMAC-секретом.

