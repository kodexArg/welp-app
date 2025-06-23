# Welp PayFlow 

## 🏢 Estructura del Sistema

### Estructura de Datos
```
UDN → Sector → IssueCategory → Issue
```

### Sistema de Permisos
```
UDN → Sector (PERMISOS AQUÍ)
```

**Datos reales:**
- **UDN**: "Km 1151", "Las Bóvedas", "Oficina Espejo"
- **Sector**: "Full", "Playa", "Administración", "Parador"  
- **Categoría**: "Compras", "Software", "Licencias", "Equipamiento Oficina", "Mobiliario", "Elementos Seguridad"

**Herencia de permisos:** Todas las **IssueCategory** e **Issues** de un sector heredan automáticamente los permisos asignados a ese sector. No hay permisos específicos por categoría.

## 👥 Tipos de Operadores

### 1. **Usuario Final**
- ✅ `can_open` | ❌ `can_comment` | ❌ `can_solve` | ❌ `can_authorize` | ❌ `can_process_payment` | ❌ `can_close`

### 2. **Técnico**
- ✅ `can_open` | ✅ `can_comment` | ✅ `can_solve` | ❌ `can_authorize` | ❌ `can_process_payment` | ❌ `can_close`

### 3. **Supervisor de Área**
- ✅ `can_open` | ✅ `can_comment` | ❌ `can_solve` | ✅ `can_authorize` | ❌ `can_process_payment` | ✅ `can_close`

### 4. **Gestor de Compras**
- ❌ `can_open` | ✅ `can_comment` | ✅ `can_solve` | ❌ `can_authorize` | ✅ `can_process_payment` | ❌ `can_close`

### 5. **Gerente/Director**
- ✅ `can_open` | ✅ `can_comment` | ❌ `can_solve` | ✅ `can_authorize` | ✅ `can_process_payment` | ✅ `can_close`

## 🔄 Estados de Solicitud

1. **🔴 Open** - Solicitud creada, esperando autorización inicial
2. **🟣 Authorized** - Solicitud autorizada, esperando presupuestos
3. **🟢 Budgeted** - Presupuestos adjuntados, esperando autorización de pago
4. **🟡 Rejected** - Presupuestos rechazados, requieren revisión
5. **🔶 Payment Authorized** - Pago autorizado, esperando proceso de facturación
6. **💰 Processing Payment** - Procesando pago/facturación
7. **📦 Shipping** - En proceso de envío/entrega
8. **⚫ Closed** - Solicitud finalizada

## 🔀 Transiciones de Estado



### Transiciones por Rol

| Desde | Hacia | Quién Puede |
|-------|-------|-------------|
| `open` | `authorized` | Supervisor, Gerente |
| `open` | `closed` | Supervisor, Gerente (cancelación) |
| `authorized` | `budgeted` | Gestor de Compras, Técnico |
| `authorized` | `closed` | Supervisor, Gerente (cancelación) |
| `budgeted` | `payment_authorized` | Supervisor, Gerente |
| `budgeted` | `rejected` | Supervisor, Gerente |
| `budgeted` | `closed` | Supervisor, Gerente (cancelación) |
| `rejected` | `budgeted` | Gestor de Compras, Técnico |
| `rejected` | `closed` | Supervisor, Gerente (cancelación) |
| `payment_authorized` | `processing_payment` | Gestor de Compras |
| `payment_authorized` | `closed` | Supervisor, Gerente (cancelación) |
| `processing_payment` | `shipping` | Gestor de Compras |
| `processing_payment` | `closed` | Supervisor, Gerente (cancelación) |
| `shipping` | `closed` | Gestor de Compras, Usuario (entrega confirmada) |

### 💬 Nota Importante sobre Comentarios

**Los comentarios NO cambian el estado de la solicitud.** Cuando alguien comenta:
- La solicitud mantiene su estado actual (`open`, `authorized`, `budgeted`, `rejected`, `payment_authorized`, `processing_payment`, `shipping`, `closed`)
- El sistema marca que hay "comentarios pendientes" o "actividad reciente"
- Pero el estado formal de la solicitud no cambia a "comentado" o "feedback"

Los comentarios son **información adicional** que acompaña las transiciones de estado, no estados en sí mismos.

**Información adicional en comentarios:**
- **"Autorizado"**: Se incluye en el comentario al cambiar a `authorized`
- **"Presupuestos adjuntados"**: Se incluye en el comentario al cambiar a `budgeted`
- **"Presupuestos rechazados"**: Se incluye en el comentario al cambiar a `rejected`
- **"Nuevos presupuestos adjuntados"**: Se incluye al volver de `rejected` a `budgeted`
- **"Pago aprobado"**: Se incluye en el comentario al cambiar a `payment_authorized`
- **"Procesando pago"**: Se incluye en el comentario al cambiar a `processing_payment`

**Nota:** El creador de la solicitud puede siempre comentar y confirmar entregas para cerrar sus propias solicitudes.

## 🎯 Casos de Uso

### Flujo Completo
1. Usuario: "Licencias Office 365 - $300" (`open`)
2. Supervisor: "Autorizado" → comentario con aprobación (`authorized`)
3. Gestor de Compras: "Presupuestos de 3 proveedores adjuntados" (`budgeted`)
4. Supervisor: "Aprobado proveedor A - $280" → comentario con decisión (`payment_authorized`)
5. Gestor de Compras: "Procesando facturación con proveedor" (`processing_payment`)
6. Gestor de Compras: "Licencias compradas, enviando credenciales" (`shipping`)
7. Usuario: "Recibido y funcionando" (`closed`)

### Flujo con Rechazo
1. Usuario: "Equipamiento nuevo - $2,000" (`open`)
2. Supervisor: "Autorizado para cotizar" (`authorized`)
3. Gestor: "Presupuestos de 3 proveedores adjuntados" (`budgeted`)
4. Supervisor: "Presupuestos muy altos, buscar alternativas" (`rejected`)
5. Gestor: "Nuevas cotizaciones con descuentos adjuntadas" (`budgeted`)
6. Supervisor: "Aprobado proveedor con descuento" (`payment_authorized`)
7. Gestor: "Procesando orden de compra" (`processing_payment`)
8. Gestor: "Equipos en camino" (`shipping`)
9. Usuario: "Recibido" (`closed`)

### Flujo Directo (Supervisor)
1. Supervisor: "Mantenimiento urgente - $400" (`open`)
2. Supervisor: "Auto-autorizado por urgencia" (`authorized`)
3. Técnico: "Cotizaciones de emergencia adjuntadas" (`budgeted`)
4. Supervisor: "Aprobado proveedor habitual" (`payment_authorized`)
5. Gestor: "Procesando pago urgente" (`processing_payment`)
6. Gestor: "Servicio realizado" (`shipping`)
7. Supervisor: "Confirmado" (`closed`)

## 🔐 Configuración de Permisos

**Sistema simplificado:** Los permisos se asignan solo a nivel **UDN** y **Sector**. Todas las categorías e issues del sector heredan automáticamente estos permisos.

```python
# Usuario Final - Puede crear solicitudes en su sector
PayFlowRoles(user=juan, udn=km_1151, sector=administracion, can_open=True)

# Técnico - Ve y gestiona presupuestos de su sector
PayFlowRoles(user=ana, udn=km_1151, sector=administracion, can_comment=True, can_solve=True)

# Supervisor - Todo su sector, autoriza y aprueba pagos
PayFlowRoles(user=carlos, udn=las_bovedas, sector=administracion, can_comment=True, can_authorize=True, can_close=True)

# Gestor de Compras - Todas las UDNs autorizadas, gestiona presupuestos y envíos
PayFlowRoles(user=maria, udn=None, sector=None, can_comment=True, can_solve=True, can_process_payment=True)

# Gerente - Toda la UDN (todos los sectores)
PayFlowRoles(user=luis, udn=km_1151, sector=None, can_open=True, can_comment=True, 
             can_authorize=True, can_process_payment=True, can_close=True)
```

## 📊 Filtrado de Solicitudes

```python
def get_user_payflow_tickets(user):
    own_tickets = Q(messages__user=user)
    user_roles = user.payflow_roles.filter(can_comment=True)
    context_tickets = Q()
    
    for role in user_roles:
        role_filter = Q()
        if role.udn: 
            role_filter &= Q(udn=role.udn)
        if role.sector: 
            role_filter &= Q(sector=role.sector)
        # Las categorías e issues heredan automáticamente del sector
        context_tickets |= role_filter
    
    # Solicitudes en proceso para gestores de compras
    if user.payflow_roles.filter(can_process_payment=True).exists():
        process_tickets = Q(status__in=['authorized', 'budgeted', 'payment_authorized', 'processing_payment', 'shipping'])
        context_tickets |= process_tickets
    
    return PayFlowTicket.objects.filter(own_tickets | context_tickets).distinct()
```

## 🔧 Interacción con el Modelo

### Lógica de Herencia de Permisos
1. **Asignación**: Los permisos se asignan solo a UDN/Sector en el modelo `PayFlowRoles`
2. **Herencia automática**: Todas las `IssueCategory` del sector heredan los permisos
3. **Herencia en cascada**: Todas las `Issues` de cada categoría heredan los permisos del sector
4. **Filtrado**: El sistema filtra automáticamente solicitudes por UDN/Sector del usuario
5. **Caso especial**: Gestor de Compras ve solicitudes autorizadas independientemente del sector

### Ejemplo de Herencia
```python
# Usuario con permisos en sector "Administración" de "Km 1151"
PayFlowRoles(user=supervisor, udn=km_1151, sector=administracion, can_authorize=True, can_close=True)

# Ve automáticamente solicitudes de TODAS las categorías del sector Administración:
# - Compras, Software, Licencias, Equipamiento, Mobiliario, etc.
# - Y todas las issues específicas dentro de cada categoría
```

### Gestor de Compras - Caso Especial
```python
# Gestor con acceso global a solicitudes autorizadas
PayFlowRoles(user=gestor, udn=None, sector=None, can_process_payment=True)

# Ve automáticamente:
# - Todas las solicitudes con estado 'authorized' o 'pending_payment'
# - Independientemente de UDN, Sector o Categoría
# - Porque su rol es procesar compras ya aprobadas
```