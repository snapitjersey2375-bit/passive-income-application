/**
 * Get the API URL for the current environment
 * - Production (Vercel): https://passive-income-application.onrender.com
 * - Development (localhost): http://localhost:8000
 */
export function getApiUrl(): string {
  if (typeof window === 'undefined') {
    // Server-side: use env var or default to Render
    return process.env.NEXT_PUBLIC_API_URL || "https://passive-income-application.onrender.com";
  }

  // Client-side: check if we're on localhost
  const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  return isLocalhost
    ? "http://localhost:8000"
    : "https://passive-income-application.onrender.com";
}
