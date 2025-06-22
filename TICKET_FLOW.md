# Sistema Welp 
Gestión de Tickets

## 📋 Introducción

**Sistema Welp**: Plataforma unificada de gestión de tickets con dos aplicaciones especializadas y arquitectura compartida.

## 🎫 Welp Desk - Mesa de Ayuda
**[Ver documentación completa →](./TICKET_FLOW_DESK.md)**

Sistema de **incidencias técnicas y soporte** con flujo simplificado.

**Casos típicos:** Soporte IT, DEBO/YPF, seguridad, mantenimiento, telefonía.

## 💰 Welp PayFlow - Gestión de Compras y Pagos
**[Ver documentación completa →](./TICKET_FLOW_PAYFLOW.md)**

Sistema de **solicitudes de pago y compras** con control de aprobaciones.

**Casos típicos:** Compra de software/licencias, equipamiento, mobiliario, viáticos.

## 🏗️ Arquitectura Compartida

### Estructura de Datos
```
UDN → Sector → IssueCategory → Issue
```

### Sistema de Permisos Simplificado
```
UDN → Sector (PERMISOS AQUÍ)
```

**Niveles de permisos:**
- **Nivel UDN**: Acceso amplio a todos los sectores (gerentes, directores)
- **Nivel Sector**: Acceso específico a un sector (supervisores, técnicos)

**Herencia automática:** Las **IssueCategory** e **Issues** heredan automáticamente los permisos del **Sector** al que pertenecen. No hay permisos específicos por categoría.

### Datos Reales
- **UDN**: "Km 1151", "Las Bóvedas", "Oficina Espejo"
- **Sectores**: "Full", "Playa", "Administración", "Parador"
- **Categorías**: DEBO, YPF, Soporte IT, Seguridad, Mantenimiento, Compras, Cartelería, Edilicios, Telefonía

### Ventajas del Sistema Simplificado
- **Gestión más simple**: Solo 2 niveles de permisos (UDN/Sector)
- **Menos configuración**: No hay que asignar permisos por cada categoría
- **Escalabilidad**: Fácil agregar nuevas categorías sin tocar permisos
- **Consistencia**: Mismo sistema en ambas aplicaciones

## 🔧 Diferencias Técnicas

| Aspecto | Welp Desk | Welp PayFlow |
|---------|-----------|--------------|
| **Estados** | 5 básicos | 7 con aprobaciones |
| **Permisos** | 5 básicos | 7 completos |
| **Complejidad** | Simplificado | Múltiples aprobaciones |
| **Enfoque** | Técnico | Financiero |
| **Sistema de Roles** | `welp_desk.Roles` | `welp_payflow.PayFlowRoles` |

## 📚 Navegación

- **[🎫 Welp Desk](./TICKET_FLOW_DESK.md)**
- **[💰 Welp PayFlow](./TICKET_FLOW_PAYFLOW.md)**

Cada documentación incluye casos de uso detallados, ejemplos de configuración, diagramas de flujo y especificaciones técnicas completas para su respectivo sistema.
