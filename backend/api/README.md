# LR(1) Parser API

Endpoints FastAPI que exponen la funcionalidad del analizador LR(1).


# Despliegue en Render.com

1. Sube tu proyecto a GitHub (incluyendo este Dockerfile y requirements.txt)
2. Ve a https://dashboard.render.com/ y crea un "Web Service"
3. Selecciona tu repo y Render detectará el Dockerfile automáticamente
4. El servicio usará el puerto 10000 (ya configurado en el Dockerfile)
5. Cuando el despliegue termine, Render te dará una URL pública

## Prueba la API en Render

Supón que la URL es `https://tu-api.onrender.com`:

```bash
curl -X POST "https://tu-api.onrender.com/api/v1/parse" \
	-H "Content-Type: application/json" \
	-d @- <<'JSON'
{
	"grammar": "S' -> D\nD -> T V\nT -> int\nT -> float\nV -> id , V\nV -> id",
	"tokens": ["float","id",",","id",",","id"]
}
JSON
```

La API responde con JSON: `first`, `closures`, `lr_table`, `derivation`.

## Documentación automática
Accede a `/docs` en tu URL de Render para ver y probar la API con Swagger UI.
