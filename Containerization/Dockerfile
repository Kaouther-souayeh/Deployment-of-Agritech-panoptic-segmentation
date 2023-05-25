FROM python:3.9
WORKDIR  /usr/src/app
COPY . ./
#RUN python -m pip install -r requirements.txt
RUN pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt
CMD ["python", "Inference_CULT.py"]
