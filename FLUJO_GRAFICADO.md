# Diagrama de Flujo del Proceso de Pagos (Welp PayFlow)

Este diagrama visualiza el ciclo de vida completo de una solicitud de compra o pago en el sistema Welp PayFlow, desde su creación hasta su cierre. Muestra las diferentes fases por las que pasa un ticket y los roles responsables de cada transición.

```mermaid
graph TD
    A[Abierto] --> B{Autorizado<br/>Supervisor<br/>Gerente}
    A --> H[Cerrado]

    B --> C{Presupuestado<br/>Gestor de Compras<br/>Técnico}
    B --> H

    C --> D{Pago Autorizado<br/>Gerente}
    C --> E{Rechazado<br/>Supervisor<br/>Gerente}
    C --> H

    E --> C
    E --> H

    D --> F{Procesando Pago<br/>Gestor de Compras}
    D --> H

    F --> G{En Envío / Entrega<br/>Gestor de Compras}
    F --> H

    G --> H{Cerrado<br/>Gestor de Compras<br/>Usuario}

    style A fill:#FFCCCC,stroke:#FF0000,stroke-width:2px;
    style B fill:#E0BBE4,stroke:#9933CC,stroke-width:2px;
    style C fill:#CCFFCC,stroke:#009900,stroke-width:2px;
    style D fill:#FFDDC1,stroke:#FF8C00,stroke-width:2px;
    style E fill:#FFFFCC,stroke:#CC9900,stroke-width:2px;
    style F fill:#ADD8E6,stroke:#4169E1,stroke-width:2px;
    style G fill:#D3D3D3,stroke:#808080,stroke-width:2px;
    style H fill:#333333,stroke:#000000,color:#FFFFFF,stroke-width:2px;
``` 