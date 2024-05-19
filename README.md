# alertmanager-notifier

[![Pipeline Status](https://gitlab.com/ix.ai/alertmanager-notifier/badges/master/pipeline.svg)](https://gitlab.com/ix.ai/alertmanager-notifier/)
[![Docker Stars](https://img.shields.io/docker/stars/ixdotai/alertmanager-notifier.svg)](https://hub.docker.com/r/ixdotai/alertmanager-notifier/)
[![Docker Pulls](https://img.shields.io/docker/pulls/ixdotai/alertmanager-notifier.svg)](https://hub.docker.com/r/ixdotai/alertmanager-notifier/)
[![Gitlab Project](https://img.shields.io/badge/GitLab-Project-554488.svg)](https://gitlab.com/ix.ai/alertmanager-notifier/)

A notifier for [alertmanager](https://github.com/prometheus/alertmanager), written in python. It supports multiple notification channels and new ones can be easily added.

## Deprecation

**Telegram Deprecation**: Starting with the version 0.5.0 of `alertmanager-notifier`, Telegram support is dropped. As such, the documentation has been updated to reflect it.

## Running a simple test

```sh
docker run --rm -it \
    -p 8899:8899 \
    -e GOTIFY_URL="https://gotify" \
    -e GOTIFY_TOKEN="your gotify token" \
    -e EXCLUDE_LABELS="yes" \
    --name alertmanager-notifier \
    registry.gitlab.com/ix.ai/alertmanager-notifier:latest
```

Run the test agains the bot:

```sh
curl -X POST -d '{"externalURL": "http://foo.bar/", "receiver": "alertmanager-notifier-webhook", "alerts": [{"status":"Testing alertmanager-notifier", "labels":{}, "annotations":{}, "generatorURL": "http://foo.bar"}]}' -H "Content-Type: application/json" localhost:8899/alert
```

## Configure alertmanager

```yml
route:
  receiver: 'alertmanager webhook'
  routes:
    - receiver: 'alertmanager-notifier-webhook'

receivers:
  - name: 'alertmanager-notifier-webhook'
    webhook_configs:
      - url: http://alertmanager-notifier:8899/alert
```

## Supported environment variables

| **Variable**        | **Default**      | **Description**                                                                                                            |
|:--------------------|:----------------:|:---------------------------------------------------------------------------------------------------------------------------|
| `GOTIFY_URL`        | -                | the URL of the [Gotify](https://gotify.net/) server |
| `GOTIFY_TOKEN`      | -                | the APP token for Gotify |
| `GOTIFY_TEMPLATE`   | `markdown.md.j2` | allows you to specify another (HTML) template, in case you've mounted it under `/templates` |
| `EXCLUDE_LABELS`    | `yes`            | set this to `no` to include the labels from the notifications |
| `LOGLEVEL`          | `INFO`           | [Logging Level](https://docs.python.org/3/library/logging.html#levels) |
| `GELF_HOST`         | -                | If set, the exporter will also log to this [GELF](https://docs.graylog.org/en/3.0/pages/gelf.html) capable host on UDP |
| `GELF_PORT`         | `12201`          | Ignored, if `GELF_HOST` is unset. The UDP port for GELF logging |
| `PORT`              | `8899`           | the port for incoming connections |
| `ADDRESS`           | `*`              | the address for the bot to listen on |

**NOTE**: If no notifier is configured, the `Null` notifier will be used and the notification will only be logged

## Gotify Priority

Gotify supports message priorities, that are also mapped to Android Importance (see [gotify/android#18](https://github.com/gotify/android/issues/18)).

If you set the *annotation* `priority` to your alert, with a number as value, this will be passed through to gotify.

**Note**: Since alertmanager supports sending multiple alerts in one message, alertmanager-notifier will always use the **highest** priority value for gotify from the batch.

## Templating

**alertmanager-notifier** supports jinja templating. take a look in the [templates/](templates/) folder for examples for that. If you want to use your own template, mount it as a volume in docker and set the `*_TEMPLATE` environment variable. The mount path should be under `/templates/` (for example `/templates/my-amazing-template`).

## Tags and Arch

The images are multi-arch, with builds for amd64, arm64, armv7 and armv6.

* `vN.N.N` - for example v0.0.1
* `latest` - always pointing to the latest version
* `dev-master` - the last build on the master branch

### Images

* Gitlab Registry: `registry.gitlab.com/ix.ai/alertmanager-notifier` - [gitlab.com/ix.ai/alertmanager-notifier](https://gitlab.com/ix.ai/alertmanager-notifier)
* GitHub Registry: `ghcr.io/ix-ai/alertmanager-notifier` [github.com/ix-ai/alertmanager-notifier](https://github.com/ix-ai/alertmanager-notifier)
* Docker Hub: `ixdotai/alertmanager-notifier` - [hub.docker.com/r/ixdotai/alertmanager-notifier](https://hub.docker.com/r/ixdotai/alertmanager-notifier)
