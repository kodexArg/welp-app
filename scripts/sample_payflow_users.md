# Usuarios de ejemplo para PayFlow

Este documento describe los usuarios ficticios creados por `init_app.py`.
Toda la configuración de UDNs, Sectores, Categorías Contables y Usuarios se carga desde `init_payflow.yaml`.

Para poblar la base de datos, ejecute el script con:

```bash
uv run scripts/init_app.py
```

Cada usuario se crea con una contraseña igual a su nombre de usuario.

> **Nota:** Los usuarios con roles `technician`, `purchase_manager` y `director` tienen acceso a todas las UDNs y sectores. Los managers acceden a múltiples UDNs especificadas. Los supervisores y usuarios finales tienen acceso a una UDN y sector específicos.

| Usuario            | Nombre completo      | UDN(s)              | Sector(es)             | Rol              |
|--------------------|---------------------|---------------------|------------------------|------------------|
| ana.cruz           | Ana Cruz            | KM 1151             | Administración         | end_user         |
| leo.gil            | Leo Gil             | KM 1151             | Operaciones            | end_user         |
| paz.diaz           | Paz Diaz            | Las Bóvedas         | Administración         | end_user         |
| juan.rios          | Juan Rios           | Las Bóvedas         | Operaciones            | end_user         |
| ines.soler         | Inés Soler          | Parador             | Parrilla               | end_user         |
| teo.vega           | Teo Vega            | Parador             | Mantenimiento          | end_user         |
| alex.rey           | Alex Rey            | Espejo              | Sistemas               | end_user         |
| sol.diaz           | Sol Diaz            | Espejo              | Compras                | end_user         |
| hugo.ruiz          | Hugo Ruiz           | VW                  | Campo                  | end_user         |
| nico.cruz          | Nico Cruz           | VW                  | Administración         | end_user         |
| dani.sanz          | Dani Sanz           | KCBD                | Operaciones            | end_user         |
| mora.rey           | Mora Rey            | KCBD                | Administración         | end_user         |
| martin.garcia      | Martín Garcia       | KM 1151             | Operaciones            | supervisor       |
| sofia.torres       | Sofía Torres        | Las Bóvedas         | Administración         | supervisor       |
| lucas.lopez        | Lucas Lopez         | Parador             | Mantenimiento          | supervisor       |
| elena.ramos        | Elena Ramos         | Espejo              | Sistemas               | supervisor       |
| santiago.fernandez | Santiago Fernandez  | KM 1151, Las Bóvedas| Todos los sectores     | manager          |
| natalia.fernandez  | Natalia Fernandez   | Todas               | Todos                  | manager          |
| felix.soto         | Felix Soto          | Todas               | Todos                  | technician       |
| julia.vega         | Julia Vega          | Todas               | Todos                  | technician       |
| catalina.rojas     | Catalina Rojas      | Todas               | Todos                  | purchase_manager |
| natalia.cobucci    | Natalia Cobucci     | Todas               | Todos                  | purchase_manager |
| mateo.vila         | Mateo Vila          | Todas               | Todos                  | director         |

## Descripción de Roles

- **end_user**: Acceso a una UDN y sector específicos para crear y gestionar sus propias solicitudes de pago
- **supervisor**: Acceso a una UDN y sector específicos con permisos adicionales de supervisión
- **manager**: Acceso completo a una o más UDNs específicas y todos sus sectores
- **technician**: Acceso técnico global a todas las UDNs y sectores
- **purchase_manager**: Gestión de compras con acceso global a todas las UDNs y sectores
- **director**: Acceso directivo completo a todas las UDNs y sectores del sistema

Catalina Rojas y Natalia Cobucci son las compradoras (purchase managers) para todo el proyecto.
