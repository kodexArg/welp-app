# Guía Oficial: Sistema de Temas Welp con Tailwind CSS 4.1

**Implementación definitiva** del theme switch usando `data-theme` en **Tailwind CSS 4.1**, con variables indirectas y referencias oficiales.

---

## 1. `/frontend/css/themes.css` — Sistema de Variables Indirectas

```css
@import "tailwindcss";

/* Mapeo oficial: Variables CSS → Utilidades Tailwind */
@theme inline {
  --color-primary: var(--primary);
  --color-secondary: var(--secondary);
  --color-bg: var(--background);
  --color-text: var(--text);
  --color-accent: var(--accent);
  --color-surface: var(--surface);
  --color-border: var(--border);
}

/* Tema por defecto (app) */
:root {
  --primary: 26 12 3;
  --secondary: 59 28 8;
  --background: 253 246 238;
  --text: 26 12 3;
  --accent: 226 123 44;
  --surface: 250 232 214;
  --border: 245 208 173;
}

/* Tema Welp Desk */
[data-theme="desk"] {
  --primary: 7 18 25;
  --secondary: 15 35 50;
  --background: 244 250 253;
  --text: 7 18 25;
  --accent: 226 123 44;
  --surface: 230 241 249;
  --border: 204 227 243;
}

/* Tema Welp Payflow */
[data-theme="payflow"] {
  --primary: 10 18 10;
  --secondary: 18 30 18;
  --background: 232 237 232;
  --text: 10 18 10;
  --accent: 226 123 44;
  --surface: 209 219 209;
  --border: 163 184 163;
}
```

**Principio clave:** Las variables en `@theme inline` **nunca cambian**. Solo cambian las variables indirectas (`--primary`, `--secondary`, etc.) según el tema activo.

---

## 2. Utilidades Generadas Automáticamente

Tailwind CSS 4.1 genera automáticamente estas clases desde `@theme inline`:

```css
/* Colores principales */
.bg-primary, .text-primary, .border-primary
.bg-secondary, .text-secondary, .border-secondary

/* Fondos y textos */
.bg-bg, .text-bg, .border-bg
.bg-text, .text-text, .border-text

/* Colores temáticos */
.bg-accent, .text-accent, .border-accent
.bg-surface, .text-surface, .border-surface
.bg-border, .text-border, .border-border
```

---

## 3. HTML / Templates — Aplicación del Tema

```html
<html lang="es" data-theme="{{ theme }}">
  <body class="bg-bg text-text">
    <nav class="bg-primary">
      <h1 class="text-secondary">Welp</h1>
    </nav>
    <main>
      <button class="bg-primary text-white hover:bg-secondary">
        Acción Principal
      </button>
      <div class="card bg-white border-border">
        <div class="card-header border-border text-text">
          Header del tema activo
        </div>
      </div>
    </main>
  </body>
</html>
```

**Valores válidos para `{{ theme }}`:**
- `null` o ausente: Tema **app** (default)
- `"desk"`: Tema **Welp Desk**
- `"payflow"`: Tema **Welp Payflow**

---

## 4. JavaScript para Cambio Dinámico

```js
(function(){
  const params = new URLSearchParams(location.search);
  const theme = params.get('theme') ||
                document.cookie.match(/theme=(\w+)/)?.[1] ||
                'app';
  
  // Solo aplicar data-theme si NO es el tema por defecto
  if (theme !== 'app') {
    document.documentElement.setAttribute('data-theme', theme);
  }
  
  document.cookie = `theme=${theme};path=/;max-age=${3600*24*30}`;
})();
```

---

## 5. Migración de Clases Existentes

**Antes (sistema anterior):**
```css
@apply bg-primary-600 text-primary-900 border-primary-200
```

**Después (sistema oficial):**
```css
@apply bg-primary text-text border-border
```

**Tabla de equivalencias:**
| Anterior | Nuevo | Uso |
|----------|-------|-----|
| `primary-50` | `bg` | Fondo principal |
| `primary-600/700` | `primary` | Color principal |
| `primary-800/900` | `secondary` | Color secundario |
| `primary-900` | `text` | Texto principal |
| `primary-200` | `border` | Bordes |
| `primary-100` | `surface` | Superficies |
| `accent-600` | `accent` | Color de acento |

---

## 6. Referencias Oficiales de Tailwind 4.1

* **Sistema `@theme inline`**: [Tailwind CSS Theme Variables](https://tailwindcss.com/docs/theme)
* **Variables CSS en Tailwind**: [CSS Variables Support](https://tailwindcss.com/docs/customizing-colors#using-css-variables)
* **Data attributes**: [Dark Mode Documentation](https://tailwindcss.com/docs/dark-mode)

---

## 7. Validación del Sistema

### ✅ Correcto
```css
/* Variables indirectas que cambian */
--primary: 26 12 3;  /* RGB sin # */

/* Mapeo estático en @theme inline */
--color-primary: var(--primary);

/* Uso en componentes */
@apply bg-primary text-text;
```

### ❌ Incorrecto
```css
/* NO usar colores directos en @theme */
@theme inline {
  --color-primary: #1a0c03;  /* ❌ */
}

/* NO usar clases numeradas */
@apply bg-primary-600;  /* ❌ */
```

---

Con esta implementación, **welp-app** tiene un sistema de temas completamente conforme con Tailwind CSS 4.1, utilizando variables indirectas para máxima flexibilidad y rendimiento. 