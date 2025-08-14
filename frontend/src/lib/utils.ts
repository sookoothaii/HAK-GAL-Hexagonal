import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Recursive function to convert snake_case keys to camelCase
export function convertToCamelCase<T>(obj: any): T {
  if (Array.isArray(obj)) {
    return obj.map(v => convertToCamelCase(v)) as any;
  } else if (obj !== null && obj.constructor === Object) {
    return Object.keys(obj).reduce((result, key) => {
      const camelCaseKey = key.replace(/([-_][a-z])/g, (group) =>
        group.toUpperCase().replace('-', '').replace('_', '')
      );
      result[camelCaseKey] = convertToCamelCase(obj[key]);
      return result;
    }, {} as { [key: string]: any }) as T;
  }
  return obj;
}
