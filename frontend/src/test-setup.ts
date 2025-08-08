/**
 * @fileoverview Test setup for Vitest
 * 
 * Global test configuration and setup utilities
 */

// Mock console methods to avoid noise in tests
global.console.warn = vi.fn();
global.console.error = vi.fn();

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Export for use in tests
export { localStorageMock };