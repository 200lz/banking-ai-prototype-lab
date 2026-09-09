import { NextResponse } from "next/server";
import {
  authConfig,
  cloudCookie,
  createPkce,
  STATE_COOKIE,
  VERIFIER_COOKIE,
} from "@/lib/auth";

export const runtime = "nodejs";
export async function GET() {
  try {
    const config = authConfig();
    const pkce = createPkce();
    const url = new URL(`${config.domain}/oauth2/authorize`);
    url.search = new URLSearchParams({
      response_type: "code",
      client_id: config.clientId,
      redirect_uri: config.redirectUri,
      scope: "openid banking-ai/query",
      state: pkce.state,
      code_challenge: pkce.challenge,
      code_challenge_method: "S256",
    }).toString();
    const response = NextResponse.redirect(url);
    response.cookies.set(STATE_COOKIE, pkce.state, {
      ...cloudCookie,
      maxAge: 600,
    });
    response.cookies.set(VERIFIER_COOKIE, pkce.verifier, {
      ...cloudCookie,
      maxAge: 600,
    });
    response.headers.set("Cache-Control", "no-store");
    return response;
  } catch {
    return NextResponse.json(
      { error: "Cloud sign-in is not configured correctly." },
      { status: 503 },
    );
  }
}
