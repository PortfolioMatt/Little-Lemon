# Little Lemon API

API RESTful desarrollada con Django REST Framework (DRF) y Djoser para gestión de restaurante con sistema de pedidos, carrito de compras y roles de usuario.

## Descripción del Proyecto

Esta API permite a diferentes tipos de usuarios (Customers, Managers, Delivery Crew) interactuar con un sistema de restaurante. Los clientes pueden navegar el menú, agregar items al carrito, realizar pedidos y consultar su historial. Los managers pueden gestionar el menú, asignar repartidores y actualizar estados de órdenes. El equipo de delivery puede ver y actualizar las entregas asignadas.

## Tecnologías Utilizadas

- **Python 3.x**
- **Django 5.x** - Framework web
- **Django REST Framework (DRF)** - API REST
- **Djoser** - Autenticación y registro de usuarios
- **djangorestframework-simplejwt** - Autenticación JWT
- **django-filter** - Filtrado de querysets
- **SQLite** - Base de datos (desarrollo)
- **Pipenv** - Gestión de dependencias y entorno virtual

## Instalación y Configuración

### Requisitos Previos
- Python 3.8 o superior
- Pipenv instalado globalmente

### Pasos de Instalación

1. **Clonar el repositorio**

2. **Instalar dependencias con Pipenv**
   ```powershell
   pipenv install
   ```

3. **Activar el entorno virtual**
   ```powershell
   pipenv shell
   ```

4. **Navegar al directorio del proyecto Django**
   ```powershell
   cd LittleLemon
   ```

5. **Aplicar migraciones**
   ```powershell
   python manage.py migrate
   ```

6. **Iniciar el servidor de desarrollo**
   ```powershell
   python manage.py runserver
   ```

7. **Acceder a la aplicación**
   - API: http://127.0.0.1:8000/api/
   - Admin: http://127.0.0.1:8000/admin/

## Estructura del Proyecto

```
LittleLemonProject/
├── Pipfile                          # Dependencias del proyecto
├── Pipfile.lock                     # Versiones exactas de dependencias
├── README.md                        # Este archivo
└── LittleLemon/              # Directorio principal del proyecto Django
    ├── manage.py                    # Utilidad de gestión de Django
    ├── db.sqlite3                   # Base de datos SQLite
    ├── LittleLemon/                 # Configuración del proyecto
    │   ├── __init__.py
    │   ├── settings.py              # Configuración general
    │   ├── urls.py                  # URLs principales
    │   ├── wsgi.py
    │   └── asgi.py
    └── LittleLemonAPI/              # Aplicación principal de la API
        ├── __init__.py
        ├── models.py                # Modelos (MenuItem, Order, Cart, etc.)
        ├── serializers.py           # Serializers de DRF
        ├── views.py                 # Vistas y lógica de endpoints
        ├── urls.py                  # URLs de la API
        ├── permissions.py           # Permisos personalizados
        ├── pagination.py            # Configuración de paginación
        ├── throttles.py             # Rate limiting
        ├── admin.py                 # Configuración del admin
        ├── apps.py
        ├── tests.py
        └── migrations/              # Migraciones de base de datos
```

## Modelos de Datos

### Category
- `slug`: Identificador único del tipo slug
- `title`: Nombre de la categoría

### MenuItem
- `name`: Nombre del plato
- `price`: Precio (decimal)
- `inventory`: Stock disponible
- `category`: Relación con Category
- `is_item_of_the_day`: Booleano para marcar el plato del día

### CartItem
- `user`: Usuario propietario del carrito
- `menu_item`: Item del menú
- `quantity`: Cantidad
- `unit_price`: Precio unitario al momento de agregar
- `added_at`: Fecha de adición

### Order
- `user`: Cliente que realizó el pedido
- `delivery_crew`: Repartidor asignado (opcional)
- `status`: Estado (0=En camino, 1=Entregado)
- `total`: Total del pedido
- `date`: Fecha de creación

### OrderItem
- `order`: Orden asociada
- `menu_item`: Item del menú
- `quantity`: Cantidad
- `unit_price`: Precio unitario al momento del pedido

### Rating
- `menu_item`: Item calificado
- `score`: Puntuación
- `comment`: Comentario opcional
- `user`: Usuario que calificó

## Roles y Permisos

### Customer (Cliente)
- Usuario autenticado sin grupos especiales
- Puede: registrarse, ver menú, agregar al carrito, hacer pedidos, ver sus pedidos

### Manager (Gerente)
- Usuario en el grupo "Manager" o superuser
- Puede: todo lo de Customer + gestionar menú, categorías, asignar repartidores, ver todas las órdenes

### Delivery Crew (Repartidor)
- Usuario en el grupo "DeliveryCrew"
- Puede: ver órdenes asignadas, actualizar estado de entrega

## Endpoints de la API

### Autenticación y Registro

| Endpoint | Método | Descripción | Permisos |
|----------|--------|-------------|----------|
| `/auth/users/` | POST | Registrar nuevo usuario | Público |
| `/auth/users/me/` | GET | Ver perfil actual | Autenticado |
| `/auth/token/login/` | POST | Obtener token (username + password) | Público |
| `/auth/token/logout/` | POST | Invalidar token | Autenticado |
| `/api/token/` | POST | Obtener JWT (access + refresh) | Público |
| `/api/token/refresh/` | POST | Renovar JWT | Público |

### Gestión de Grupos

| Endpoint | Método | Descripción | Permisos |
|----------|--------|-------------|----------|
| `/api/groups/manager/users` | GET | Listar managers | Manager/Admin |
| `/api/groups/manager/users` | POST | Asignar usuario a Manager | Manager/Admin |
| `/api/groups/manager/users/{userId}/` | DELETE | Quitar de Manager | Manager/Admin |
| `/api/groups/delivery-crew/users` | GET | Listar repartidores | Manager/Admin |
| `/api/groups/delivery-crew/users` | POST | Asignar usuario a Delivery Crew | Manager/Admin |
| `/api/groups/delivery-crew/users/{userId}/` | DELETE | Quitar de Delivery Crew | Manager/Admin |

### Menú y Categorías

| Endpoint | Método | Descripción | Permisos |
|----------|--------|-------------|----------|
| `/api/menu-items/` | GET | Listar items del menú | Público |
| `/api/menu-items/` | POST | Crear item | Manager/Admin |
| `/api/menu-items/{id}/` | GET | Ver detalle de item | Público |
| `/api/menu-items/{id}/` | PUT/PATCH | Actualizar item | Manager/Admin |
| `/api/menu-items/{id}/` | DELETE | Eliminar item | Manager/Admin |
| `/api/menu-items/item-of-the-day/` | GET | Ver item del día | Público |
| `/api/menu-items/item-of-the-day/set/` | POST | Establecer item del día | Manager/Admin |
| `/api/categories/` | GET | Listar categorías | Público |
| `/api/categories/` | POST | Crear categoría | Manager/Admin |
| `/api/categories/{id}/` | GET | Ver categoría | Público |
| `/api/categories/{id}/` | PUT/PATCH | Actualizar categoría | Manager/Admin |
| `/api/categories/{id}/` | DELETE | Eliminar categoría | Manager/Admin |

### Carrito de Compras

| Endpoint | Método | Descripción | Permisos |
|----------|--------|-------------|----------|
| `/api/cart/menu-items/` | GET | Ver carrito actual | Customer |
| `/api/cart/menu-items/` | POST | Agregar item al carrito | Customer |
| `/api/cart/menu-items/` | DELETE | Vaciar carrito completo | Customer |
| `/api/cart/menu-items/{id}/` | GET | Ver item del carrito | Customer |
| `/api/cart/menu-items/{id}/` | PATCH/PUT | Actualizar cantidad | Customer |
| `/api/cart/menu-items/{id}/` | DELETE | Eliminar item del carrito | Customer |

### Órdenes

| Endpoint | Método | Descripción | Permisos |
|----------|--------|-------------|----------|
| `/api/orders/` | GET | Listar órdenes (filtradas por rol) | Autenticado |
| `/api/orders/` | POST | Crear orden desde carrito | Customer |
| `/api/orders/{id}/` | GET | Ver detalle de orden | Autenticado* |
| `/api/orders/{id}/` | PATCH/PUT | Actualizar orden/asignar repartidor | Manager/Delivery** |
| `/api/orders/{id}/` | DELETE | Eliminar orden | Manager/Admin |

*Customer ve solo sus órdenes, Manager ve todas, Delivery Crew ve las asignadas a él  
**Manager puede asignar delivery_crew y cambiar status; Delivery Crew solo puede cambiar status en órdenes asignadas

## Funcionalidades Implementadas (21 Criterios)

### ✅ Gestión de Usuarios y Grupos
1. **Admin puede asignar usuarios al grupo Manager** - `/api/groups/manager/users`
2. **Acceso al grupo Manager con token de admin** - Endpoint protegido con `IsManagerOrAdmin`
3. **Admin puede agregar items del menú** - POST `/api/menu-items/` (Manager/Admin only)
4. **Admin puede agregar categorías** - POST `/api/categories/` (Manager/Admin only)
5. **Managers pueden iniciar sesión** - Djoser + Token/JWT
6. **Managers pueden actualizar item del día** - POST `/api/menu-items/item-of-the-day/set/`
7. **Managers pueden asignar usuarios a delivery crew** - `/api/groups/delivery-crew/users`
8. **Managers pueden asignar órdenes al delivery crew** - PATCH `/api/orders/{id}/` con `delivery_crew`

### ✅ Delivery Crew
9. **Delivery crew puede acceder a órdenes asignadas** - GET `/api/orders/` (filtrado automático)
10. **Delivery crew puede marcar orden como entregada** - PATCH `/api/orders/{id}/` con `status: 1`

### ✅ Customers (Clientes)
11. **Customers pueden registrarse** - POST `/auth/users/`
12. **Customers pueden iniciar sesión y obtener tokens** - POST `/auth/token/login/` o `/api/token/`
13. **Customers pueden ver todas las categorías** - GET `/api/categories/`
14. **Customers pueden ver todos los items del menú** - GET `/api/menu-items/`
15. **Customers pueden filtrar items por categoría** - GET `/api/menu-items/?category={id}`
16. **Customers pueden paginar items del menú** - `?page=1&number_pages=10`
17. **Customers pueden ordenar items por precio** - `?ordering=price` o `?ordering=-price`
18. **Customers pueden agregar items al carrito** - POST `/api/cart/menu-items/`
19. **Customers pueden ver items en el carrito** - GET `/api/cart/menu-items/`
20. **Customers pueden crear pedidos** - POST `/api/orders/` (convierte carrito en orden)
21. **Customers pueden ver sus propios pedidos** - GET `/api/orders/`

## Filtrado, Búsqueda y Ordenamiento

### Menu Items
- **Filtros**: `?category=1`, `?price_min=10`, `?price_max=50`, `?inventory_min=5`
- **Búsqueda**: `?search=pasta`
- **Ordenamiento**: `?ordering=price`, `?ordering=-price`, `?ordering=inventory`
- **Paginación**: `?page=2&number_pages=20`

### Orders
- **Filtros**: `?status=0`, `?user={id}`, `?delivery_crew={id}`, `?total_min=50`, `?date_min=2025-11-01T00:00:00Z`
- **Búsqueda**: `?search=username` (busca en customer y delivery crew)
- **Ordenamiento**: `?ordering=-date`, `?ordering=total`, `?ordering=status`
- **Paginación**: `?page=1&number_pages=15`

## Ejemplos de Uso

### 1. Registro de Usuario
```http
POST /auth/users/
Content-Type: application/json

{
  "username": "maria",
  "password": "SecurePass123!",
  "email": "maria@example.com"
}
```

### 2. Login (Obtener Token)
```http
POST /auth/token/login/
Content-Type: application/json

{
  "username": "maria",
  "password": "SecurePass123!"
}

Response:
{
  "auth_token": "abc123def456..."
}
```

### 3. Agregar Item al Carrito
```http
POST /api/cart/menu-items/
Authorization: Token abc123def456...
Content-Type: application/json

{
  "menu_item_id": 5,
  "quantity": 2
}
```

### 4. Crear Orden desde Carrito
```http
POST /api/orders/
Authorization: Token abc123def456...
```

### 5. Asignar Repartidor a Orden (Manager)
```http
PATCH /api/orders/12/
Authorization: Token {manager-token}
Content-Type: application/json

{
  "delivery_crew": "repartidor1",
  "status": 0
}
```

### 6. Marcar Orden como Entregada (Delivery Crew)
```http
PATCH /api/orders/12/
Authorization: Token {delivery-token}
Content-Type: application/json

{
  "status": 1
}
```

## Autenticación

El proyecto soporta dos métodos de autenticación:

### Token Authentication (Recomendado para este proyecto)
- Header: `Authorization: Token {your-token}`
- Obtener token: POST `/auth/token/login/`
- Invalidar token: POST `/auth/token/logout/`

### JWT (Alternativa)
- Header: `Authorization: Bearer {access-token}`
- Obtener tokens: POST `/api/token/`
- Renovar: POST `/api/token/refresh/`

## Testing

Puedes probar la API con:
- **Navegador**: API navegable de DRF en http://127.0.0.1:8000/api/
- **Insomnia/Postman**: Importar colección de endpoints
- **curl/PowerShell**: Scripts de línea de comandos

### Ejemplo con PowerShell
```powershell
# Login
$response = Invoke-RestMethod -Uri http://127.0.0.1:8000/auth/token/login/ `
  -Method POST -ContentType "application/json" `
  -Body '{"username":"maria","password":"SecurePass123!"}'

$token = $response.auth_token

# Ver menú
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/menu-items/" `
  -Headers @{ Authorization = "Token $token" }
```

## Notas Importantes

- **Base de datos**: SQLite (desarrollo). Para producción, considerar PostgreSQL/MySQL.
- **Seguridad**: Los tokens tienen validez indefinida con Token Auth. JWT expira según configuración.
- **Grupos**: "Manager" y "Delivery Crew" se crean automáticamente al usar los endpoints de gestión (get_or_create).
- **Customers**: No requieren grupo; cualquier usuario autenticado sin grupos especiales es Customer.
- **Admin site**: Disponible en `/admin/` para gestión directa de datos.

## Dependencias Principales

Ver `Pipfile` para lista completa. Principales:
- django
- djangorestframework
- djoser
- djangorestframework-simplejwt
- django-filter

## Contacto y Soporte

Para dudas o issues relacionados con el proyecto, consultar la documentación oficial:
- [Django](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Djoser](https://djoser.readthedocs.io/)

## Licencia

Este proyecto es parte de un ejercicio educativo.
