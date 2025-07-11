# Usuarios de ejemplo para PayFlow

Este documento describe los usuarios ficticios creados por `init_payflow_users.py`.
Ejecute el script con:

```bash
uv run scripts/init_payflow_users.py
```

Cada usuario se crea con contraseña igual a su nombre de usuario. Se asume que las UDN y sectores ya fueron cargados con `init_payflow.py`.

> **Nota:** Algunos usuarios tienen acceso a múltiples sectores y/o UDN según su rol. Los técnicos y la gestora de compras tienen acceso total a todas las combinaciones de UDN y sector. Los managers acceden a todos los sectores de su UDN. Los supervisores y usuarios finales pueden tener varios sectores en una misma UDN.

| Usuario            | Nombre completo      | UDN(s)         | Sector(es)                        | Rol              |
|--------------------|---------------------|---------------|------------------------------------|------------------|
| pato.moro          | Pato Moro           | KM 1151       | Administración, Operaciones        | end_user         |
| vino.tes           | Vino Tes            | KM 1151       | Operaciones, Administración        | end_user         |
| coco.zen           | Coco Zen            | KM 1151       | Administración, Operaciones        | end_user         |
| lili.per           | Lili Per            | Las Bóvedas   | Operaciones, Administración        | end_user         |
| pepe.kid           | Pepe Kid            | Parador       | Parrilla, Mantenimiento           | end_user         |
| pili.box           | Pili Box            | KCBD          | Operaciones                        | end_user         |
| yoyo.vis           | Yoyo Vis            | Espejo        | Sistemas                           | end_user         |
| colo.yin           | Colo Yin            | VW            | Campo                              | end_user         |
| luna.mani          | Luna Mani           | Todas         | Todos                              | technician       |
| tito.ban           | Tito Ban            | Todas         | Todos                              | technician       |
| dani.tux           | Dani Tux            | Todas         | Todos                              | technician       |
| riko.caz           | Riko Caz            | Todas         | Todos                              | technician       |
| riki.lux           | Riki Lux            | KM 1151       | Administración, Operaciones, Otro* | supervisor       |
| lola.pox           | Lola Pox            | KM 1151       | Operaciones, Administración, Otro* | supervisor       |
| mimo.san           | Mimo San            | Las Bóvedas   | Administración, Operaciones, Otro* | supervisor       |
| nana.hup           | Nana Hup            | Parador       | Mantenimiento, Parrilla, Otro*     | supervisor       |
| teo.mor            | Teo Mor             | KM 1151       | Todos los sectores                 | manager          |
| jupi.vec           | Jupi Vec            | Las Bóvedas   | Todos los sectores                 | manager          |
| melo.tux           | Melo Tux            | Espejo        | Todos los sectores                 | manager          |
| natalia.cobucci    | Natalia Cobucci     | Todas         | Todos                              | purchase_manager |

*"Otro" indica que el usuario tiene acceso a un sector adicional dentro de la misma UDN, elegido aleatoriamente para simular variedad.

- Los técnicos y la gestora de compras tienen acceso a todas las UDN y sectores (roles múltiples).
- Los managers tienen acceso a todos los sectores de su UDN (roles múltiples).
- Supervisores y usuarios finales pueden tener hasta 2 o 3 sectores en la misma UDN.

Natalia Cobucci es la única compradora (purchase manager) para todo el proyecto.
