/**
 * File: vitest.setup.ts
 * 
 * Purpose:
 * Initializes the testing environment before tests run, importing necessary
 * DOM testing extensions.
 * 
 * Key Functionalities:
 * - Import @testing-library/jest-dom for extended DOM matchers in Vitest
 * 
 * Inputs:
 * - None
 * 
 * Outputs:
 * - None
 * 
 * Interacting Files / Modules:
 * - vitest.config.ts
 */
import "@testing-library/jest-dom/vitest";
