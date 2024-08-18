import wretch from "wretch";
import { retry } from "wretch/middlewares";

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_BASE_URL;

export const api = wretch(BASE_URL);

export type TResponse<T = unknown, E = unknown> = {
  ok?: boolean;
  error?: E;
  response?: T;
};
