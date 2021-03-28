FROM mongo-express:latest

COPY ./compose/mongo-express/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./compose/mongo-express/start_mongo_express.js /start_mongo_express.js
RUN sed -i 's/\r//' /start_mongo_express.js
RUN chmod +x /start_mongo_express.js

ENTRYPOINT ["/entrypoint.sh"]