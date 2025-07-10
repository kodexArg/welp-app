# Usuarios de ejemplo para PayFlow

Este documento describe los usuarios ficticios creados por `init_payflow_users.py`.
Ejecute el script con:

```bash
uv run scripts/init_payflow_users.py
```

Cada usuario se crea con contraseña igual a su nombre de usuario. Se asume que las UDN y sectores ya fueron cargados con `init_payflow.py`.

| Usuario | Nombre completo | UDN | Sector | Rol |
|---------|-----------------|-----|--------|-----|
| pato.moro | Pato Moro | KM 1151 | Administración | end_user |
| vino.tes | Vino Tes | KM 1151 | Operaciones | end_user |
| coco.zen | Coco Zen | Las Bóvedas | Administración | end_user |
| lili.per | Lili Per | Las Bóvedas | Operaciones | end_user |
| pepe.kid | Pepe Kid | Parador | Parrilla | end_user |
| pili.box | Pili Box | KCBD | Operaciones | end_user |
| yoyo.vis | Yoyo Vis | Espejo | Sistemas | end_user |
| colo.yin | Colo Yin | VW | Campo | end_user |
| luna.mani | Luna Mani | KM 1151 | Administración | technician |
| tito.ban | Tito Ban | KM 1151 | Operaciones | technician |
| dani.tux | Dani Tux | Las Bóvedas | Operaciones | technician |
| riko.caz | Riko Caz | Parador | Mantenimiento | technician |
| riki.lux | Riki Lux | KM 1151 | Administración | supervisor |
| lola.pox | Lola Pox | KM 1151 | Operaciones | supervisor |
| mimo.san | Mimo San | Las Bóvedas | Administración | supervisor |
| nana.hup | Nana Hup | Parador | Mantenimiento | supervisor |
| teo.mor | Teo Mor | KM 1151 | — | manager |
| jupi.vec | Jupi Vec | Las Bóvedas | — | manager |
| melo.tux | Melo Tux | Espejo | — | manager |
| natalia.cobucci | Natalia Cobucci | — | — | purchase_manager |

Natalia Cobucci es la única compradora (purchase manager) para todo el proyecto.
