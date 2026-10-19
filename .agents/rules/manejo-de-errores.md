---
trigger: always_on
description: Regla para la gestión, corrección y registro de errores reportados por el usuario
---

# Manejo y Registro de Errores

Cuando el usuario reporte un error por el chat y solicite su corrección, se debe seguir estrictamente este flujo:

1. **Revisión y Corrección**:
   - Analizar el problema planteado por el usuario.
   - Implementar la corrección correspondiente en el proyecto. (Si no estamos en modo plan, si lo estamos solo generar el plan y esperar la orden para proceder)

2. **Registro en `log-de-errores.md` (Nuevo Error)**:
   - Crear una entrada en `log-de-errores.md` (en la raíz del proyecto) con la siguiente estructura:
     - **Fecha y Hora**: Momento exacto del registro (`AAAA-MM-DD HH:MM`).
     - **Título**: Nombre representativo y claro del error.
     - **Descripción**: Explicación detallada del problema detectado y su contexto.
     - **Solución**: Detalle de los cambios o correcciones aplicadas.

3. **Reincidencia o Ajuste (El error persiste o tiene fallos)**:
   - Si el usuario vuelve a indicar por el chat que la corrección aún tiene errores o que no quedó bien resuelto:
     - **No crear una entrada nueva duplicada**.
     - **Localizar y modificar la entrada existente** en `log-de-errores.md`.
     - **Mejorar la descripción**: Ampliar y precisar la explicación con el nuevo feedback proporcionado.
     - **Actualizar la solución**: Reemplazar o complementar la solución con el nuevo ajuste implementado y la fecha/hora de actualización.

4. ** Aprendizaje**:
    - Revisar este log antes de aplicar cambios
    - Revisar este log antes de hacer un plan
    El objetivo es no cometer los mismo errores