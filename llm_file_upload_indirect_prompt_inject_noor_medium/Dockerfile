
FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir numpy==1.24.4
RUN pip install --no-cache-dir torch==2.1.2+cpu torchvision==0.16.2+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install --no-cache-dir transformers==4.37.2 flask python-dotenv

EXPOSE 9000

CMD ["python", "app.py"]
