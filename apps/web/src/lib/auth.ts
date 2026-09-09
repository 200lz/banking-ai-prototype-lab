import { createHash, randomBytes, timingSafeEqual } from "node:crypto";

export const ACCESS_COOKIE = "lab_access_token";
export const STATE_COOKIE = "lab_oauth_state";
export const VERIFIER_COOKIE = "lab_pkce_verifier";

export function authConfig(
  env: Record<string, string | undefined> = process.env,
) {
  if (env.WEB_AUTH_MODE !== "cognito")
    throw new Error("Cloud authentication is not configured");
  const domain = new URL(env.COGNITO_DOMAIN || "");
  const app = new URL(env.APP_BASE_URL || "");
  if (
    domain.protocol !== "https:" ||
    app.protocol !== "https:" ||
    domain.username ||
    domain.password ||
    app.username ||
    app.password ||
    domain.search ||
    domain.hash ||
    app.search ||
    app.hash ||
    !env.COGNITO_CLIENT_ID
  ) {
    throw new Error("Cloud authentication requires trusted HTTPS origins");
  }
  return {
    domain: domain.origin,
    app: app.origin,
    clientId: env.COGNITO_CLIENT_ID,
    redirectUri: `${app.origin}/api/auth/callback`,
  };
}

export function createPkce() {
  const verifier = randomBytes(32).toString("base64url");
  return {
    verifier,
    challenge: createHash("sha256").update(verifier).digest("base64url"),
    state: randomBytes(32).toString("base64url"),
  };
}

export function validState(
  expected: string | undefined,
  actual: string | null,
) {
  if (
    !expected ||
    !actual ||
    expected.length !== actual.length ||
    expected.length > 128 ||
    !/^[A-Za-z0-9_-]+$/.test(actual)
  )
    return false;
  return timingSafeEqual(Buffer.from(expected), Buffer.from(actual));
}

export function validAccessToken(
  value: string | undefined,
): string | undefined {
  return value &&
    value.length <= 16_000 &&
    /^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/.test(value)
    ? value
    : undefined;
}

export const cloudCookie = {
  httpOnly: true,
  secure: true,
  sameSite: "lax" as const,
  path: "/",
};
