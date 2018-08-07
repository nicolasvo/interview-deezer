FROM python:3

WORKDIR /home
COPY . .

RUN pip install pipenv
RUN pipenv install --system

ENTRYPOINT ["/bin/bash"]
CMD ["run.sh"]
