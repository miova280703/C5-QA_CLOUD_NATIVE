/**
 * Genera datos de productos con Faker (semilla fija = reproducible).
 * Coherente con el Dia 1 (datos sinteticos) y el Dia 2 (servicio-tienda).
 * Escribe datos/db.json que el servidor sirve en /api/productos.
 */
import { faker } from '@faker-js/faker';
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Semilla fija: los datos salen iguales en cada maquina y corrida
faker.seed(2128);

const CATEGORIAS = ['clavas', 'pelotas', 'diabolos', 'fuego'];
const TOTAL = 30;

const NOMBRES_MALABARES = {
  clavas: ['Clava Profesional PX3', 'Clava de Entrenamiento', 'Clava Neón LED', 'Clava de Madera Clásica', 'Clava Multicolor', 'Clava Mini'],
  pelotas: ['Pelota Métrica de Semilla', 'Pelota de Silicona Stage', 'Pelota LED Recargable', 'Pelota de Trapo Malleable', 'Pelota Glow in Dark', 'Pelota Rusa'],
  diabolos: ['Diábolo Triple Rodamiento', 'Diábolo Juggling Medium', 'Baquetas de Aluminio', 'Cuerda de Kevlar Diábolo', 'Diábolo Gigante Pro', 'Set Diábolo Principiante'],
  fuego: ['Antorcha de Fuego Profesional', 'Poi de Fuego Doble', 'Abanico de Fuego 5 Mechas', 'Aro de Fuego', 'Cinta Kevlar 50mm', 'Dragón Staff de Fuego']
};

const productos = Array.from({ length: TOTAL }, (_, i) => {
  const categoria = CATEGORIAS[i % CATEGORIAS.length];
  const listaNombres = NOMBRES_MALABARES[categoria];
  const nombreBase = listaNombres[i % listaNombres.length];
  return {
    id: i + 1,
    nombre: `${nombreBase} ${faker.hacker.abbreviation()}`,
    categoria,
    precio: Number(faker.commerce.price({ min: 20, max: 500 })),
    descripcion: `Equipo profesional para malabarismo de categoría: ${categoria}`,
    stock: faker.number.int({ min: 0, max: 60 }),
  };
});

const db = { productos, pedidos: [] };

mkdirSync(__dirname, { recursive: true });
const rutaArchivo = join(__dirname, 'db.json');
writeFileSync(rutaArchivo, JSON.stringify(db, null, 2), 'utf-8');

console.log(`datos/db.json generado con ${productos.length} productos (semilla fija).`);
