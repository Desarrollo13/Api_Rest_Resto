# 🍽️ Restaurante API

![CI](https://github.com/Desarrollo13/Api_Rest_Resto/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-REST_Framework-green)
![Tests](https://img.shields.io/badge/Tests-61_passing-brightgreen)
![Deploy](https://img.shields.io/badge/Deploy-Render-purple)

API REST completa para gestión de restaurante construida con Django REST Framework. Incluye autenticación JWT con roles, gestión de órdenes, pagos, reservas y reportes de ventas.

---

## 🌐 Links

| | URL |
|---|---|
| **API** | https://restaurante-api-e5mv.onrender.com/api/ |
| **Documentación** | https://restaurante-api-e5mv.onrender.com/api/docs/ |
| **Dashboard** | https://dashboard-restaurante-theta.vercel.app |

---

## ✨ Funcionalidades

### Backend
- 🔐 Autenticación JWT con refresh y logout seguro
- 👥 5 roles con permisos diferenciados (administrador, gerente, mozo, cocinero, cajero)
- 🍽️ Gestión de menú por categorías
- 🪑 Mesas y reservas con validación de horarios
- 📋 Flujo completo de órdenes por estado
- 💰 Pagos con comprobante (efectivo, tarjeta, transferencia)
- 📊 Reportes de ventas (diarias, mensuales, por mozo, productos más vendidos)
- ✅ 61 pruebas unitarias

### Dashboard (Frontend)
- 📊 Resumen del día con gráficos
- 📋 Órdenes en tiempo real con refresh automático
- 🍽️ CRUD completo de menú
- 👤 Gestión de usuarios y roles
- 📈 Reportes de productos más vendidos
- 👥 Rendimiento por mozo

---

## 🛠️ Stack tecnológico

### Backend
| Tecnología | Uso |
|---|---|
| Django 4.2 | Framework principal |
| Django REST Framework | API REST |
| SimpleJWT | Autenticación JWT |
| drf-spectacular | Documentación OpenAPI/Swagger |
| PostgreSQL | Base de datos en producción |
| Gunicorn + Whitenoise | Servidor de producción |
| python-decouple | Variables de entorno |

### Frontend
| Tecnología | Uso |
|---|---|
| React + Vite | Framework frontend |
| Tailwind CSS | Estilos |
| Recharts | Gráficos |
| Axios | HTTP client |
| React Router | Navegación |
| React Hot Toast | Notificaciones |

### DevOps
| Tecnología | Uso |
|---|---|
| Render | Deploy del backend + PostgreSQL |
| Vercel | Deploy del frontend |
| GitHub Actions | CI/CD — tests automáticos |

---

## 🚀 Instalación local

### Requisitos
- Python 3.12
- Node.js 18+
- Git

### Backend

```bash
# 1. Clonar el repositorio
git clone https://github.com/Desarrollo13/Api_Rest_Resto.git
cd Api_Rest_Resto

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 5. Aplicar migraciones
python manage.py migrate

# 6. Crear superusuario
python manage.py createsuperuser

# 7. Correr el servidor
python manage.py runserver
```

### Frontend

```bash
# 1. Clonar el repositorio del dashboard
git clone https://github.com/Desarrollo13/dashboard-restaurante.git
cd dashboard-restaurante

# 2. Instalar dependencias
npm install

# 3. Configurar variables de entorno
cp .env.example .env
# Editar VITE_API_URL con la URL del backend

# 4. Correr en desarrollo
npm run dev
```

---

## 🧪 Tests

```bash
# Correr toda la suite
python manage.py test users.tests mesas.tests menu.tests ordenes.tests reportes.tests --verbosity=2

# Resultado esperado
Ran 61 tests in Xs
OK
```

| Módulo | Tests |
|---|:---:|
| Autenticación JWT | 7 |
| Permisos por rol | 9 |
| Órdenes y estados | 13 |
| Pagos y facturación | 10 |
| Reportes de ventas | 11 |
| Reservas y mesas | 11 |
| **Total** | **61** |

---

## 📡 Endpoints principales

### Autenticación
```
POST /api/auth/token/       Login — obtener tokens
POST /api/auth/refresh/     Renovar access token
POST /api/auth/logout/      Logout — invalidar token
```

### Recursos
```
GET/POST   /api/menu/              Menú (público para GET)
GET/POST   /api/ordenes/           Órdenes
PATCH      /api/ordenes/{id}/estado/   Cambiar estado
POST       /api/ordenes/{id}/pagar/    Registrar pago
GET        /api/ordenes/{id}/comprobante/ Ver comprobante
GET/POST   /api/mesas/             Mesas
GET/POST   /api/reservas/          Reservas
GET/POST   /api/usuarios/          Usuarios (solo admin)
```

### Reportes
```
GET /api/reportes/resumen/           Resumen del día
GET /api/reportes/ventas/diarias/    Ventas por fecha
GET /api/reportes/ventas/mensuales/  Ventas mensuales
GET /api/reportes/productos/         Productos más vendidos
GET /api/reportes/mozos/             Rendimiento por mozo
```

---

## 🔐 Roles y permisos

| Acción | Admin | Gerente | Mozo | Cocinero | Cajero |
|---|:---:|:---:|:---:|:---:|:---:|
| Gestionar usuarios | ✅ | ❌ | ❌ | ❌ | ❌ |
| Gestionar menú | ✅ | ✅ | ❌ | ❌ | ❌ |
| Crear órdenes | ✅ | ✅ | ✅ | ❌ | ✅ |
| Ver órdenes | ✅ | ✅ | 👁️ | ✅ | ✅ |
| Cambiar estado orden | ✅ | ✅ | ✅ | ✅ | ❌ |
| Registrar pagos | ✅ | ❌ | ❌ | ❌ | ✅ |
| Ver reportes | ✅ | ✅ | ❌ | ❌ | ❌ |

> 👁️ El mozo solo ve sus propias órdenes

---

## 📁 Estructura del proyecto

```
restaurante/
├── .github/
│   └── workflows/
│       └── ci.yml          ← GitHub Actions
├── users/                  ← Autenticación y roles
├── menu/                   ← Menú y categorías
├── mesas/                  ← Mesas y reservas
├── ordenes/                ← Órdenes y pagos
├── reportes/               ← Reportes de ventas
├── restaurant/             ← Configuración Django
├── requirements.txt
├── build.sh                ← Script de deploy
└── .env.example
```

---

## 👨‍💻 Autor

**Cristian** — [@Desarrollo13](https://github.com/Desarrollo13)