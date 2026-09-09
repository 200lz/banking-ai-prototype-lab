// Amplify build variables are not automatically available to Next.js SSR.
// Export only non-secret configuration; never copy all process.env values.
import { writeFileSync } from "node:fs";

const names = [
  "WEB_AUTH_MODE",
  "API_BASE_URL",
  "COGNITO_DOMAIN",
  "COGNITO_CLIENT_ID",
  "APP_BASE_URL",
];
const lines = names.map((name) => {
  const value = process.env[name];
  if (!value || /[\r\n]/.test(value)) {
    throw new Error(`Missing or invalid deployment configuration: ${name}`);
  }
  return `${name}=${JSON.stringify(value)}`;
});
writeFileSync("apps/web/.env.production", `${lines.join("\n")}\n`, { mode: 0o600 });
