FROM mongo:7-jammy

RUN apt-get update \
  && apt-get install -y --no-install-recommends gettext-base \
  && rm -rf /var/lib/apt/lists/*

COPY init-mongo.js.template /docker-entrypoint-initdb.d/init-mongo.js.template
COPY docker-entrypoint-gen.sh /usr/local/bin/docker-entrypoint-gen.sh
RUN chmod +x /usr/local/bin/docker-entrypoint-gen.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint-gen.sh"]
CMD ["mongod"]