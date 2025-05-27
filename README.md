# Carro Seguidor linea  🏎️
🔥¡Emocionate y compite con nuestro carrlo seguidor de linea! 🔥 

> ## **Consideraciones** 💻
Para que el entorno grafico y el juego se ejecuten de forma correcta es necesario:
* **Crear el entorno virtual** <br>
python3 -m venv hola <br>
* **Activar entorno virtual** <br>
source hola/bin/activate <br>

Instalar modulos y librerias necesarias
* **Instalar pygame** <br>
pip install pygame <br>
* **Instalar entorno grafico y Tkinter**
sudo apt install python3-tk

> ## **Importante para Docker** 🐳
* **Construir el la imagen docker** <br>
docker build -t usta_racing <br>
* **Runearlo el imagen docker**<br>
xhost +local:docker
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  juego-tk
