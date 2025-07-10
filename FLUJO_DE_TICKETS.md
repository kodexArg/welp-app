# Sistema de Tickets Welp

## ¿Qué es Welp?

Welp es la plataforma central para gestionar todas tus solicitudes, desde problemas técnicos hasta compras y pagos. El sistema se divide en dos grandes áreas para mantener todo organizado:

-   **Welp Desk (Soporte Técnico)**: Para reportar incidencias técnicas, problemas con sistemas (DEBO/YPF), solicitar mantenimiento o resolver fallos de telefonía.
-   **Welp PayFlow (Gestión de Compras)**: Para solicitar la compra de productos o servicios, como licencias de software, equipamiento, mobiliario o viáticos.

Este documento es una guía rápida para entender cómo funciona el sistema. Para detalles más técnicos, puedes consultar la documentación específica de [Welp Desk](./TICKET_FLOW_DESK.md) o [Welp PayFlow](./TICKET_FLOW_PAYFLOW.md).

## ¿Cómo se organizan las solicitudes?

Todas las solicitudes se organizan según tu **Unidad de Negocio (UDN)** y tu **Sector**. Por ejemplo, "UDN: Km 1151, Sector: Administración". Esto asegura que tu solicitud llegue directamente a las personas correctas para gestionarla.

## ¿Qué puedes hacer en el sistema? (Roles)

Tu rol en la empresa determina qué acciones puedes realizar dentro de Welp.

### 1. **Usuario Final**
-   Creas solicitudes (tickets) para ti.
-   Puedes ver el estado de tus propias solicitudes, añadir comentarios y confirmar cuando has recibido un producto o servicio para cerrar el ticket.

### 2. **Técnico**
-   Puedes crear tus propias solicitudes.
-   Una vez que una solicitud de tu área es autorizada, puedes verla para buscar y adjuntar presupuestos.

### 3. **Supervisor de Área**
-   Puedes crear solicitudes y ver todas las de tu UDN y Sector.
-   Eres el encargado de dar la **primera autorización** a las solicitudes de tu equipo. También puedes rechazarlas si no proceden.

### 4. **Gestor de Compras**
-   Puedes crear tus propias solicitudes.
-   Gestionas todas las solicitudes de compra que ya han sido autorizadas.
-   Te encargas de adjuntar presupuestos, procesar los pagos y coordinar el envío o entrega.

### 5. **Gerente / Director**
-   Tienes los mismos permisos que un Supervisor.
-   Adicionalmente, eres el único que puede dar la **autorización final de pago** sobre una solicitud que ya tiene presupuestos.

## 🔄 Flujo desde la compra al pago

### Fases de la Solicitud

1.  **🔴 Abierto**: La solicitud ha sido creada y está esperando la aprobación inicial del Supervisor.
2.  **🟣 Autorizado**: El Supervisor ha aprobado la solicitud. Ahora, el equipo de Compras o un Técnico puede buscar presupuestos.
3.  **🟢 Presupuestado**: Se han adjuntado los presupuestos a la solicitud. Ahora se necesita la aprobación final del Gerente para el pago.
4.  **🟡 Rechazado**: Los presupuestos o la solicitud fueron rechazados. Se necesita revisar y, posiblemente, adjuntar nuevas opciones.
5.  **🔶 Pago Autorizado**: ¡Luz verde! El Gerente ha aprobado el pago del presupuesto seleccionado.
6.  **💰 Procesando Pago**: El Gestor de Compras está realizando los trámites para pagar al proveedor.
7.  **📦 En Envío / Entrega**: El producto o servicio ya ha sido pagado y está en camino o en proceso de entrega.
8.  **⚫ Cerrado**: La solicitud se ha completado. El usuario ha confirmado la recepción.

### Tabla de Pasos y Responsables

| Si el ticket está... | El siguiente paso es... | ¿Quién puede hacerlo? |
|----------------------|-------------------------|--------------------------|
| `Abierto`            | `Autorizarlo`           | Supervisor, Gerente      |
| `Abierto`            | `Cerrarlo (cancelar)`   | Supervisor, Gerente      |
| `Autorizado`         | `Adjuntar presupuestos` | Gestor de Compras, Técnico |
| `Presupuestado`      | `Autorizar el pago`     | Gerente                  |
| `Presupuestado`      | `Rechazarlo`            | Supervisor, Gerente      |
| `Rechazado`          | `Adjuntar nuevos presupuestos` | Gestor de Comras, Técnico |
| `Pago Autorizado`    | `Procesar el pago`      | Gestor de Compras        |
| `Procesando Pago`    | `Marcar como enviado`   | Gestor de Compras        |
| `En Envío / Entrega` | `Cerrarlo`              | Gestor de Compras, Usuario |

### Una nota sobre los comentarios

Añadir un comentario a una solicitud **no cambia su estado**. Los comentarios son para añadir información, hacer preguntas o dar seguimiento, pero la fase del ticket (Abierto, Autorizado, etc.) solo cambia cuando se realiza una acción específica (como autorizar o adjuntar un presupuesto).

## Ejemplo Práctico: Compra de un Ordenador

1.  **Ana (Usuario Final)** crea una solicitud: "Necesito un nuevo ordenador para diseño". El ticket queda en estado **Abierto**.
2.  **Carlos (Supervisor)** revisa la solicitud y la aprueba. El ticket cambia a **Autorizado**.
3.  **María (Gestor de Compras)** ve el ticket autorizado y busca tres presupuestos. Los adjunta. El ticket cambia a **Presupuestado**.
4.  **Luisa (Gerente)** revisa los presupuestos, elige uno y aprueba el pago. El ticket cambia a **Pago Autorizado**.
5.  **María (Gestor de Compras)** realiza la compra y el pago. El ticket cambia a **Procesando Pago**.
6.  Una vez pagado, María actualiza el estado a **En Envío / Entrega**.
7.  Cuando el ordenador llega, **Ana (Usuario Final)** confirma la recepción y el ticket se marca como **Cerrado**. 