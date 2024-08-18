import wretch from "wretch";
import { retry } from "wretch/middlewares";

// TODO: Update base api url
const BASE_URL = "/";

export const api = wretch(BASE_URL).middlewares([retry({ maxAttempts: 3 })]);

export type TResponse<T = unknown, E = unknown> = {
  ok?: boolean;
  error?: E;
  response?: T;
};
