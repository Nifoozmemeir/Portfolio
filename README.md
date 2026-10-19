<div align="center">

# JERSdev · Portfolio

**Portfolio personal, Full Stack Developer (Python · Django) y Game Developer (Unity · C#).**

Experiencia, proyectos, habilidades y contacto en una sola página, en español, inglés y portugués.

[![Sitio](https://img.shields.io/badge/jersdev.com-online-667eea?style=for-the-badge&logo=googlechrome&logoColor=white)](https://jersdev.com)

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=flat-square&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-FF9900?style=flat-square&logo=amazonwebservices&logoColor=white)

</div>

---

## 🛠️ Instalación local

> Todos los comandos van en **Git Bash**, salvo el de Redis, que va en **Ubuntu de WSL**.

**Requisitos:** Python 3.12, PostgreSQL y WSL con Ubuntu.

**1. Clonar el repo**
```sh
git clone https://github.com/Nifoozmemeir/Portfolio.git
cd Portfolio
```

**2. Crear y activar el entorno virtual**
```sh
py -m venv myvenv
source myvenv/Scripts/activate
```

**3. Instalar las dependencias**
```sh
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**4. Configurar las variables de entorno**
```sh
cp .env.example .env
```
Y completar el `.env` con tus datos.

**5. Levantar Redis** (en Ubuntu de WSL)
```sh
sudo apt install redis-server
redis-cli ping   # tiene que responder PONG
```

**6. Crear las tablas y un usuario para el admin**
```sh
py manage.py migrate
py manage.py createsuperuser
```

**7. Compilar las traducciones**
```sh
wsl msgfmt -o resources/locale/en/LC_MESSAGES/django.mo resources/locale/en/LC_MESSAGES/django.po
wsl msgfmt -o resources/locale/pt/LC_MESSAGES/django.mo resources/locale/pt/LC_MESSAGES/django.po
```

**8. Levantar el server** 🎉
```sh
py manage.py runserver
```
Entrá a http://127.0.0.1:8000 y cargá el contenido desde el admin.

**Tests**
```sh
py manage.py test
```

---

<div align="center">

Hecho con ☕ y 🐍 por **Julián Rosas Sandillú** · [jersdev.com](https://jersdev.com) · [LinkedIn](https://linkedin.com/in/julian-ers/) · [GitHub](https://github.com/Nifoozmemeir)

</div>
