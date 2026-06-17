FROM python:3.13.5-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user

RUN chown -R user:user /app /tmp

USER user
ENV PATH="/home/user/.local/bin:$PATH"
ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_MAX_UPLOAD_SIZE=50
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

COPY --chown=user requirements.txt ./
RUN pip3 install --user -r requirements.txt

COPY --chown=user . .

EXPOSE 7860

HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health


ENTRYPOINT ["streamlit", "run", "app.py"]

# ENTRYPOINT ["streamlit", "run", "app.py", \
#             "--server.port=7860", \
#             "--server.address=0.0.0.0"]