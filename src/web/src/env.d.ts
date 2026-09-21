// Types for the NG_APP_* env vars injected by @ngx-env/builder (see angular.md §4).
declare interface Env {
  readonly NODE_ENV: string;
  readonly NG_APP_API_BASE_URL: string;
  [key: string]: string | undefined;
}

declare interface ImportMeta {
  readonly env: Env;
}
