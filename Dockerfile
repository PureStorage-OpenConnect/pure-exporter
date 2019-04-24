FROM python:3-alpine
COPY pure_fa_collector.py /
COPY pure_fb_collector.py /
COPY pure_prom_exporter.py /
COPY requirements.txt /
RUN pip install -r requirements.txt
RUN pip install gunicorn
COPY gunicorn.conf /
EXPOSE 9091
CMD [ "gunicorn", "-c", "gunicorn.conf", "pure_prom_exporter:app" ]
