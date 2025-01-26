# Usar imagem base do Python
FROM python:3.9-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    # Dependências gráficas
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libpng-dev \
    libx11-dev \
    libxss-dev \
    libgl1-mesa-dev \
    # Dependências de áudio
    alsa-utils \
    pulseaudio \
    # Dependências de codec e driver
    vainfo \
    libva2 \
    libva-drm2 \
    libva-x11-2 \
    # Utilitários extras
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Configurações de áudio e vídeo
ENV PULSE_SERVER=unix:/run/user/1000/pulse/native
ENV SDL_AUDIODRIVER=pulseaudio
ENV AUDIODEV=default
ENV DISPLAY=:0

# Copiar arquivos do projeto
COPY . /app

# Instalar dependências Python
RUN pip install --no-cache-dir \
    pygame \
    numpy \
    pgzero

# Comando de execução
CMD ["python", "main.py"]
