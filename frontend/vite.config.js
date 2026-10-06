import { defineConfig } from "vite"

const apiPaths = [
  "/auth",
  "/usuarios",
  "/sedes",
  "/mesas",
  "/productos",
  "/proveedores",
  "/inventario",
  "/pedidos",
  "/admin",
]

export default defineConfig({
  server: {
    host: "127.0.0.1",
    port: 5175,
    strictPort: true,
    proxy: Object.fromEntries(
      apiPaths.map((path) => [
        path,
        { target: "http://127.0.0.1:8000", changeOrigin: true },
      ]),
    ),
  },
})
