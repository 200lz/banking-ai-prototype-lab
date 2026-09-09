import { NextResponse } from "next/server";
import {
  ACCESS_COOKIE,
  authConfig,
  cloudCookie,
  STATE_COOKIE,
  VERIFIER_COOKIE,
} from "@/lib/auth";
import { sameOrigin } from "@/lib/proxy";

export async function POST(request: Request) {
  if (!sameOrigin(request, process.env.APP_BASE_URL))
    return NextResponse.json(
      { error: "Invalid request origin." },
      { status: 403 },
    );
  try {
    const config = authConfig();
    const url = new URL(`${config.domain}/logout`);
    url.search = new URLSearchParams({
      client_id: config.clientId,
      logout_uri: config.app,
    }).toString();
    const response = NextResponse.redirect(url, 303);
    for (const name of [ACCESS_COOKIE, STATE_COOKIE, VERIFIER_COOKIE])
      response.cookies.set(name, "", { ...cloudCookie, maxAge: 0 });
    response.headers.set("Cache-Control", "no-store");
    return response;
  } catch {
    return NextResponse.json(
      { error: "Cloud sign-out is not configured." },
      { status: 503 },
    );
  }
}
