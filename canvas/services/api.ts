import wretch from "wretch";
export const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_BASE_URL;
export const WS_BASE_URL = process.env.NEXT_PUBLIC_WEBSOCKET_BASE_URL;

export const api = wretch(BASE_URL).options({
  cache: "no-store", // Disables caching
});
