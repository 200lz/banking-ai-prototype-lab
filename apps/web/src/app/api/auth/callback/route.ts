import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { z } from "zod";
import {
  ACCESS_COOKIE,
  authConfig,
  cloudCookie,
  STATE_COOKIE,
  validAccessToken,
  validState,
  VERIFIER_COOKIE,
} from "@/lib/auth";
import { readBoundedBody } from "@/lib/proxy";

export const runtime = "nodejs";
export async function GET(request: Request) {
  try {
    const config = authConfig();
    const jar = await cookies();
    const params = new URL(request.url).searchParams;
    const verifier = jar.get(VERIFIER_COOKIE)?.value;
    const code = params.get("code");
    const response = NextResponse.redirect(`${config.app}/?auth=failed`);
    response.cookies.set(STATE_COOKIE, "", { ...cloudCookie, maxAge: 0 });
    response.cookies.set(VERIFIER_COOKIE, "", { ...cloudCookie, maxAge: 0 });
    response.headers.set("Cache-Control", "no-store");
    if (
      !validState(jar.get(STATE_COOKIE)?.value, params.get("state")) ||
      !verifier ||
      !/^[A-Za-z0-9_-]{43}$/.test(verifier) ||
      !code ||
      code.length > 2048
    )
      return response;
    const tokenResponse = await fetch(`${config.domain}/oauth2/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        client_id: config.clientId,
        code,
        redirect_uri: config.redirectUri,
        code_verifier: verifier,
      }),
      cache: "no-store",
      redirect: "error",
      signal: AbortSignal.timeout(10_000),
    });
    if (!tokenResponse.ok) return response;
    const parsed = z
      .object({
        access_token: z.string(),
        expires_in: z.number().positive().max(86_400),
        token_type: z.literal("Bearer"),
      })
      .safeParse(JSON.parse(await readBoundedBody(tokenResponse.body, 32_000)));
    if (!parsed.success || !validAccessToken(parsed.data.access_token))
      return response;
    response.headers.set("Location", config.app);
    response.cookies.set(ACCESS_COOKIE, parsed.data.access_token, {
      ...cloudCookie,
      sameSite: "strict",
      maxAge: Math.min(parsed.data.expires_in, 3600),
    });
    return response;
  } catch {
    return NextResponse.json(
      { error: "Sign-in failed. Return to the lab and try again." },
      { status: 502 },
    );
  }
}
