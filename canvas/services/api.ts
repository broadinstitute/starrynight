import wretch from "wretch";
import { retry } from "wretch/middlewares";

export const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_BASE_URL;
export const WS_BASE_URL = process.env.NEXT_PUBLIC_WEBSOCKET_BASE_URL;

export const api = wretch(BASE_URL).options({
  cache: "no-store", // Disables caching
});

export type TResponse<T = unknown, E = unknown> = {
  ok?: boolean;
  error?: E;
  response?: T;
};
