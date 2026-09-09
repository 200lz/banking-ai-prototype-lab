import { cookies } from "next/headers";
import { ACCESS_COOKIE, validAccessToken } from "@/lib/auth";

export async function GET() {
  const cloud = process.env.WEB_AUTH_MODE === "cognito";
  const jar = await cookies();
  return Response.json(
    {
      cloud,
      authenticated:
        !cloud || Boolean(validAccessToken(jar.get(ACCESS_COOKIE)?.value)),
    },
    { headers: { "Cache-Control": "no-store" } },
  );
}
