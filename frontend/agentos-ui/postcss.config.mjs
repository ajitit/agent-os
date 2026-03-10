/**
 * File: postcss.config.mjs
 * 
 * Purpose:
 * Configures PostCSS transformations for the frontend application's styling.
 * 
 * Key Functionalities:
 * - Load the modern `@tailwindcss/postcss` plugin to process Tailwind directives
 * 
 * Inputs:
 * - CSS files containing Tailwind directives
 * 
 * Outputs:
 * - Compiled frontend CSS
 * 
 * Interacting Files / Modules:
 * - src.app.globals.css
 */
const config = {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};

export default config;
