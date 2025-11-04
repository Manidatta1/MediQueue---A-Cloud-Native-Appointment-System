FROM apache/airflow:2.9.0

USER airflow
RUN pip install --no-cache-dir psycopg2-binary requests

# Copy DAGs
COPY dags/ /opt/airflow/dags/

EXPOSE 8080



# # Default command — initialize DB, create user, and start webserver + scheduler
# CMD bash -c "airflow db init && \
#     airflow users create -u admin -p admin -f Air -l Flow -r Admin -e admin@example.com && \
#     airflow webserver & airflow scheduler"
