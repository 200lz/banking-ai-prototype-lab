import { cookies } from "next/headers";
import { ACCESS_COOKIE, validAccessToken } from "@/lib/auth";
import { proxyQuery } from "@/lib/proxy";

export const runtime = "nodejs";
export async function POST(request: Request) {
  const jar = await cookies();
  return proxyQuery(request, {
    apiBase: process.env.API_BASE_URL || "http://127.0.0.1:8000",
    appBase: process.env.APP_BASE_URL,
    cloud: process.env.WEB_AUTH_MODE === "cognito",
    token: validAccessToken(jar.get(ACCESS_COOKIE)?.value),
  });
}
