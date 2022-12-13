FROM python:3.10-slim
COPY . ./
RUN pip install -r requirements.txt --no-cache
RUN pyinstaller --onefile --noconfirm --clean --name hachivsd-linux main.py