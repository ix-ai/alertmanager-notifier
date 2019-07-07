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
* `LOGLEVEL` (default: `INFO`)
