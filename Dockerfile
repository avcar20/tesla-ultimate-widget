FROM python:3.9-slim
WORKDIR /app
# Gerekli kütüphaneleri yükle [cite: 46]
RUN pip install paho-mqtt plyer
COPY teslax.py .
CMD ["python", "teslax.py"]