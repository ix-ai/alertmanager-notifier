# alertmanager-telegram-bot


[![pipeline status](https://git.ix.ai/docker/alertmanager-telegram-bot/badges/master/pipeline.svg)](https://git.ix.ai/docker/alertmanager-telegram-bot/commits/master)

A simple webserver in Flask, that translates alertmanager alerts into telegram messages.

**WARNING!** This is for testing only. It is not considered production ready!

## Running a simple test
```
docker run --rm -it \
    -p 9119:9119 \
    -e TELEGRAM_TOKEN="your token" \
    -e TELEGRAM_CHAT_ID="your chat id" \
    --name alertmanager-telegram-bot \
    hub.ix.ai/docker/alertmanager-telegram-bot:latest
```

Run the test agains the bot:
```
curl -X POST -d '{"alerts": [{"status":"Testing alertmanager-telegram-bot", "labels":[], "annotations":[], "generatorURL": "http://localhost"}]}' -H "Content-Type: application/json" localhost:9119/alert
```

## Configure alertmanager
```
route:
  receiver: 'telegram alerts'
  routes:
    - receiver: 'telegram-webhook'

receivers:
  - name: 'telegram-webhook'
    webhook_configs:
      - url: http://alertmanager-telegram-bot:9119/alert
```

## Supported environment variables:

* `TELEGRAM_TOKEN` (no default) - see the [Telegram documentation](https://core.telegram.org/bots#creating-a-new-bot) how to get a new token
* `TELEGRAM_CHAT_ID` (no default) - see this question on [stackoverflow](https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id)
* `GELF_HOST` (no default) - if set, the exporter will also log to this [GELF](https://docs.graylog.org/en/3.0/pages/gelf.html) capable host on UDP
* `GELF_PORT` (defaults to `12201`) - the port to use for GELF logging
* `LOGLEVEL` (default: `INFO`)
* `PORT` (default: 9119) - the port for the bot
