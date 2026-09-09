import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { test } from "node:test";
import {
  authConfig,
  cloudCookie,
  createPkce,
  validAccessToken,
  validState,
} from "../src/lib/auth";

test("PKCE uses unique verifier and state with S256 challenge", () => {
  const first = createPkce();
  const second = createPkce();
  assert.equal(first.verifier.length, 43);
  assert.equal(
    first.challenge,
    createHash("sha256").update(first.verifier).digest("base64url"),
  );
  assert.notEqual(first.verifier, second.verifier);
  assert.notEqual(first.state, second.state);
});

test("OAuth state fails closed on missing, mismatched and non-ASCII input", () => {
  assert.equal(validState("abc", "abc"), true);
  assert.equal(validState(undefined, "abc"), false);
  assert.equal(validState("abc", null), false);
  assert.equal(validState("abc", "abd"), false);
  assert.equal(validState("abc", "ébc"), false);
});

test("auth configuration uses trusted HTTPS origins and fixed callback", () => {
  const env = {
    WEB_AUTH_MODE: "cognito",
    COGNITO_DOMAIN: "https://lab.auth.us-east-1.amazoncognito.com",
    APP_BASE_URL: "https://lab.example.com",
    COGNITO_CLIENT_ID: "public-client",
  };
  assert.equal(
    authConfig(env).redirectUri,
    "https://lab.example.com/api/auth/callback",
  );
  assert.throws(() =>
    authConfig({ ...env, APP_BASE_URL: "http://lab.example.com" }),
  );
  assert.throws(() =>
    authConfig({ ...env, COGNITO_DOMAIN: "https://user:pass@example.com" }),
  );
  assert.throws(() => authConfig({ ...env, WEB_AUTH_MODE: "local" }));
});

test("access token shape blocks header injection and cookies are server-only", () => {
  assert.equal(validAccessToken("a.b.c"), "a.b.c");
  for (const value of [
    "Bearer a.b.c",
    "a.b.c\r\nX-Foo: yes",
    "not-a-jwt",
    undefined,
  ])
    assert.equal(validAccessToken(value), undefined);
  assert.equal(cloudCookie.httpOnly, true);
  assert.equal(cloudCookie.secure, true);
  assert.equal(cloudCookie.sameSite, "lax");
});
