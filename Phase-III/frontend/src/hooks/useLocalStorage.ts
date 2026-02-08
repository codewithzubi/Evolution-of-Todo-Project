// [Task]: T015, [From]: specs/002-task-ui-frontend/spec.md#FR-003
// Generic localStorage hook with SSR safety and JSON serialization

import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for reading/writing to localStorage with SSR support
 * [Task]: T015, [From]: specs/002-task-ui-frontend/spec.md#FR-003
 *
 * @template T - Type of value stored in localStorage
 * @param key - localStorage key
 * @param initialValue - Default value if key not found or corrupted
 * @returns Tuple of [value, setter, remover]
 *
 * @example
 * const [count, setCount, removeCount] = useLocalStorage('count', 0);
 */
export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T) => void, () => void] {
  // State to store our value
  const [storedValue, setStoredValue] = useState<T>(initialValue);
  const [isInitialized, setIsInitialized] = useState(false);

  // Initialize value from localStorage on mount (client-side only)
  useEffect(() => {
    try {
      // Avoid running on server
      if (typeof window === 'undefined') {
        setIsInitialized(true);
        return;
      }

      // Get from localStorage by key
      const item = window.localStorage.getItem(key);

      if (item) {
        try {
          // Parse stored JSON value
          setStoredValue(JSON.parse(item) as T);
        } catch (error) {
          // If JSON parsing fails, treat as corrupted data
          console.warn(`Failed to parse localStorage value for key "${key}":`, error);
          setStoredValue(initialValue);
        }
      } else {
        setStoredValue(initialValue);
      }
    } catch (error) {
      console.warn(`Failed to access localStorage for key "${key}":`, error);
      setStoredValue(initialValue);
    } finally {
      setIsInitialized(true);
    }
  }, [key, initialValue]);

  // Return a wrapped version of useState's setter function that persists to localStorage
  const setValue = useCallback(
    (value: T) => {
      try {
        // Allow value to be a function like useState
        const valueToStore = value instanceof Function ? value(storedValue) : value;

        // Save state
        setStoredValue(valueToStore);

        // Avoid running on server
        if (typeof window === 'undefined') {
          return;
        }

        // Save to localStorage
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      } catch (error) {
        console.warn(`Failed to set localStorage value for key "${key}":`, error);
      }
    },
    [key, storedValue]
  );

  // Return a wrapped version of useState's remover function
  const removeValue = useCallback(() => {
    try {
      // Remove state
      setStoredValue(initialValue);

      // Avoid running on server
      if (typeof window === 'undefined') {
        return;
      }

      // Remove from localStorage
      window.localStorage.removeItem(key);
    } catch (error) {
      console.warn(`Failed to remove localStorage value for key "${key}":`, error);
    }
  }, [key, initialValue]);

  // Return uninitialized values until hydration completes to prevent hydration mismatch
  if (!isInitialized) {
    return [initialValue, setValue, removeValue];
  }

  return [storedValue, setValue, removeValue];
}
