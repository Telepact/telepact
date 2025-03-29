export function encodeBase64(uint8Array: Uint8Array): string {
    if (typeof window !== 'undefined') {
      // Browser environment
      return btoa(String.fromCharCode(...uint8Array));
    } else {
      // Node.js environment
      return Buffer.from(uint8Array).toString('base64');
    }
}
  
export function decodeBase64(base64String: string): Uint8Array {
    if (typeof window !== 'undefined') {
      // Browser environment
      return Uint8Array.from(atob(base64String), c => c.charCodeAt(0));
    } else {
      // Node.js environment
      return Uint8Array.from(Buffer.from(base64String, 'base64'));
    }
}