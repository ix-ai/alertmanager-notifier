FROM public.ecr.aws/docker/library/alpine:latest@sha256:a8560b36e8b8210634f77d9f7f9efd7ffa463e380b75e2e74aff4511df3ef88c as builder

COPY alertmanager-notifier/requirements.txt /work/alertmanager-notifier/requirements.txt

ENV CRYPTOGRAPHY_DONT_BUILD_RUST="1"

RUN set -xeu; \
    mkdir -p /work/wheels; \
    apk add \
      python3-dev \
      py3-pip \
      openssl-dev \
      gcc \
      musl-dev \
      libffi-dev \
      make \
      openssl-dev \
      cargo \
    ; \
    pip3 install -U --break-system-packages \
      wheel \
      pip

RUN pip3 wheel --prefer-binary -r /work/alertmanager-notifier/requirements.txt -w /work/wheels

FROM public.ecr.aws/docker/library/alpine:latest@sha256:a8560b36e8b8210634f77d9f7f9efd7ffa463e380b75e2e74aff4511df3ef88c

LABEL org.opencontainers.image.authors="alertmanager-notifier@docker.egos.tech" \
      org.opencontainers.image.source="https://gitlab.com/ix.ai/alertmanager-notifie" \
      org.opencontainers.image.url="egos.tech/alertmanager-notifier"

COPY --from=builder /work /

RUN set -xeu; \
    ls -lashi /wheels; \
    apk add --no-cache py3-pip; \
    pip3 install \
      -U \
      --break-system-packages \
      --no-index \
      --no-cache-dir \
      --find-links /wheels \
      --requirement /alertmanager-notifier/requirements.txt \
    ; \
    rm -rf /wheels

COPY alertmanager-notifier/ /alertmanager-notifier
COPY templates/ /templates
COPY alertmanager-notifier.sh /usr/local/bin/alertmanager-notifier.sh

EXPOSE 9119

ENTRYPOINT ["/usr/local/bin/alertmanager-notifier.sh"]
