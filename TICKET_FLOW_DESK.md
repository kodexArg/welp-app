# Welp Desk 

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
- **Categoría**: "DEBO", "YPF", "Soporte IT", "Seguridad", "Mantenimiento", "Cartelería", "Edilicios", "Telefonía y Comunicación"

**Herencia de permisos:** Todas las **IssueCategory** e **Issues** de un sector heredan automáticamente los permisos asignados a ese sector. No hay permisos específicos por categoría.

## 👥 Tipos de Operadores

### 1. **Usuario Final**
- ✅ `can_open` | ❌ `can_comment` | ❌ `can_solve` | ❌ `can_reject` | ❌ `can_close`

### 2. **Técnico**
- ✅ `can_open` | ✅ `can_comment` | ✅ `can_solve` | ❌ `can_reject` | ❌ `can_close`

### 3. **Supervisor de Área**
- ✅ `can_open` | ✅ `can_comment` | ✅ `can_solve` | ✅ `can_reject` | ❌ `can_close`

### 4. **Gerente/Director**
- ✅ `can_open` | ✅ `can_comment` | ❌ `can_solve` | ✅ `can_reject` | ✅ `can_close`

## 🔄 Estados del Ticket

1. **🔴 Open** - Estado inicial
2. **🟢 Solved** - Marcado como resuelto
3. **🟡 Rejected** - Rechazado para revisión
4. **⚫ Closed** - Finalizado

## 🔀 Transiciones de Estado

### Transiciones por Rol

| Desde | Hacia | Quién Puede |
|-------|-------|-------------|
| `open` | `solved` | Técnico, Supervisor |
| `open` | `rejected` | Supervisor, Gerente |
| `open` | `closed` | Gerente |
| `solved` | `rejected` | Supervisor, Gerente |
| `solved` | `closed` | Gerente |
| `rejected` | `solved` | Técnico, Supervisor |
| `rejected` | `closed` | Gerente |

### 💬 Nota Importante sobre Comentarios

**Los comentarios NO cambian el estado del ticket.** Cuando alguien comenta:
- El ticket mantiene su estado actual (`open`, `solved`, `rejected`, `closed`)
- El sistema marca que hay "comentarios pendientes" o "actividad reciente"
- Pero el estado formal del ticket no cambia a "comentado" o "feedback"

Los comentarios son **información adicional** que acompaña las transiciones de estado, no estados en sí mismos.

**Nota:** El creador del ticket puede siempre comentar y cerrar sus propios tickets sin permisos explícitos.

## 🎯 Casos de Uso

### Flujo Básico
1. Usuario: "Internet no funciona" (`open`)
2. Técnico: "Router reiniciado, funcionando" (`solved`)
3. Supervisor: "Confirmado" (`closed`)

### Flujo con Escalamiento
1. Usuario: "Sistema DEBO inoperativo" (`open`)
2. Técnico L2: "Servicio reiniciado" (`solved`)
3. Supervisor: "Falta documentar causa" (`rejected`)
4. Técnico L2: "Documentación completada" (`solved`)
5. Supervisor: "Aprobado" (`closed`)

## 🔐 Configuración de Permisos

**Sistema simplificado:** Los permisos se asignan solo a nivel **UDN** y **Sector**. Todas las categorías e issues del sector heredan automáticamente estos permisos.

```python
# Usuario Final - Puede crear tickets en su sector
Roles(user=juan, udn=km_1151, sector=full, can_open=True)

# Técnico - Ve y gestiona todos los tickets de su sector
Roles(user=carlos, udn=km_1151, sector=full, can_comment=True, can_solve=True)

# Supervisor - Todo su sector
Roles(user=ana, udn=las_bovedas, sector=full, can_comment=True, can_solve=True, can_reject=True)

# Gerente - Toda la UDN (todos los sectores)
Roles(user=luis, udn=km_1151, sector=None, can_open=True, can_comment=True, can_reject=True, can_close=True)
```

## 📊 Filtrado de Tickets

```python
def get_user_tickets(user):
    own_tickets = Q(messages__user=user)  # Tickets propios
    user_roles = user.welp_roles.filter(can_comment=True)
    context_tickets = Q()
    
    for role in user_roles:
        role_filter = Q(udn=role.udn)
        if role.sector: 
            role_filter &= Q(sector=role.sector)
        # Las categorías e issues heredan automáticamente del sector
        context_tickets |= role_filter
    
    return Ticket.objects.filter(own_tickets | context_tickets).distinct()
```

## 🔧 Interacción con el Modelo

### Lógica de Herencia de Permisos
1. **Asignación**: Los permisos se asignan solo a UDN/Sector en el modelo `Roles`
2. **Herencia automática**: Todas las `IssueCategory` del sector heredan los permisos
3. **Herencia en cascada**: Todas las `Issues` de cada categoría heredan los permisos del sector
4. **Filtrado**: El sistema filtra automáticamente tickets por UDN/Sector del usuario

### Ejemplo de Herencia
```python
# Usuario con permisos en sector "Full" de "Km 1151"
Roles(user=tecnico, udn=km_1151, sector=full, can_comment=True, can_solve=True)

# Ve automáticamente tickets de TODAS las categorías del sector Full:
# - DEBO, YPF, Soporte IT, Seguridad, Mantenimiento, etc.
# - Y todas las issues específicas dentro de cada categoría
```