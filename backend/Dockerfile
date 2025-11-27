FROM eclipse-temurin:17-jre
WORKDIR /app
COPY target/fanqie-backend-0.1.0.jar app.jar
EXPOSE 8080
ENV DB_HOST=localhost DB_PORT=3306 DB_NAME=fanqie DB_USERNAME=root DB_PASSWORD=password
ENTRYPOINT ["java","-jar","/app/app.jar"]