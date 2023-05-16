FROM python:3.9
WORKDIR ./usr/src/app
COPY . ./
COPY S2-2017-T31TFM-meanstd.pkl ./BindMounting/Input/
#RUN python -m pip install -r requirements.txt
RUN pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements.txt
CMD ["python", "Inference_CULT.py"]
