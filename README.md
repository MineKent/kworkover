# Kwork Offer Analyzer

Сервис отслеживает новые предложения в Kwork, считает процент совпадения с вашим стеком, отправляет подходящие заявки в Telegram и умеет:

- сгенерировать отклик через модель из `OpenRouter`
- отправить этот отклик обратно в Kwork по кнопке из Telegram

## Как это работает

1. Playwright открывает страницу проектов Kwork с уже сохраненной авторизацией.
2. Сервис забирает новые карточки заявок.
3. `sentence-transformers` строит эмбеддинги вашего профиля навыков и текста заявки.
4. Если совпадение выше порога, заявка уходит вам в Telegram.
5. По кнопке `Generate reply` сервис отправляет заявку в `OpenRouter` и получает черновик отклика.
6. По кнопке `Send to Kwork` Playwright подставляет ответ в форму на сайте и отправляет его.

## Быстрый старт

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
copy .env.example .env
```

Заполните `.env`.

## Важный шаг: авторизация Kwork

Сервис использует `storage_state`, чтобы работать от вашего аккаунта.

1. Один раз сохраните сессию в `./data/kwork-storage.json`.
2. Для этого можно использовать готовый скрипт `scripts/save_kwork_session.py`:

```bash
python scripts/save_kwork_session.py
```

## Запуск

```bash
python main.py
```

Если файл `data/kwork-storage.json` еще не создан, сервис все равно запустится и сможет читать заявки без авторизации, но отправка откликов в Kwork будет недоступна, пока вы не выполните:

```bash
python scripts/save_kwork_session.py
```

## Переменные окружения

- `TELEGRAM_BOT_TOKEN` - токен бота
- `TELEGRAM_CHAT_ID` - ваш Telegram chat id
- `TELEGRAM_PROXY` - необязательно, `http://login:password@host:port` или `socks5://host:port`, если `api.telegram.org` недоступен напрямую
- `KWORK_STORAGE_STATE_JSON` - необязательно, содержимое `kwork-storage.json` целиком; удобно для Render, где нет постоянного диска на free плане
- `SKILLS_PROFILE` - список навыков в свободной форме, например: `Создание сайтов без CMS, Telegram-боты, Telegram Mini App`
- `OPENROUTER_API_KEY` - ключ OpenRouter
- `OPENROUTER_MODEL` - модель для генерации отклика
- `KWORK_MIN_MATCH_PERCENT` - минимальный процент совпадения

## Deploy на Render

Проще всего деплоить как `Background Worker` через Docker.

1. Залейте проект в GitHub.
2. В Render создайте `New +` -> `Background Worker`.
3. Выберите репозиторий; Render увидит `render.yaml` и `Dockerfile`.
4. В `Environment` добавьте переменные из `.env`.
5. Для авторизации Kwork локально получите файл сессии:

```bash
python scripts/save_kwork_session.py
```

6. Откройте `data/kwork-storage.json`, скопируйте весь JSON и вставьте его в переменную `KWORK_STORAGE_STATE_JSON` в Render.
7. Запустите deploy.

Замечания по Render:

- На free плане worker может останавливаться при ограничениях платформы, поэтому это подходит больше для теста.
- Без `KWORK_STORAGE_STATE_JSON` сервис сможет искать заявки, но не сможет отправлять отклики от вашего аккаунта.
- Если у вас не открывается `api.telegram.org`, задайте `TELEGRAM_PROXY` в Render.

## Замечания

- Верстка Kwork может меняться, поэтому CSS-селекторы вынесены в `.env`.
- Для экономии можно начать с бесплатных моделей OpenRouter, затем переключиться на более сильную платную модель.
- Автоотправка ответа зависит от актуальности селекторов формы на Kwork.
