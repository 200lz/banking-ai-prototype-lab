import { querySchema, responseSchema } from "./contracts";

export const MAX_REQUEST_BYTES = 24_000;
export const MAX_RESPONSE_BYTES = 1_000_000;

export function apiDestination(base: string, cloud: boolean): URL {
  const url = new URL(base);
  if (
    url.username ||
    url.password ||
    url.search ||
    url.hash ||
    !["http:", "https:"].includes(url.protocol)
  ) {
    throw new Error("Invalid API configuration");
  }
  const localHosts = ["localhost", "127.0.0.1", "[::1]", "api"];
  if (
    (cloud && url.protocol !== "https:") ||
    (!cloud && !localHosts.includes(url.hostname))
  ) {
    throw new Error("API destination violates environment boundary");
  }
  url.pathname = `${url.pathname.replace(/\/$/, "")}/v1/query`;
  return url;
}

export function sameOrigin(request: Request, appBase?: string): boolean {
  const origin = request.headers.get("origin");
  if (!origin) return false;
  try {
    const incoming = new URL(origin);
    if (appBase) return incoming.origin === new URL(appBase).origin;
    // Next.js may canonicalize Request.url to localhost even when the browser
    // used 127.0.0.1. In local mode accept only a matching loopback Host header;
    // forwarded-host headers and arbitrary DNS names never establish trust.
    const internal = new URL(request.url);
    const expectedHost = request.headers.get("host") || internal.host;
    return (
      ["localhost", "127.0.0.1", "[::1]"].includes(incoming.hostname) &&
      incoming.host === expectedHost &&
      incoming.protocol === internal.protocol
    );
  } catch {
    return false;
  }
}

export async function readBoundedBody(
  body: ReadableStream<Uint8Array> | null,
  limit: number,
): Promise<string> {
  if (!body) throw new Error("Missing request body");
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let total = 0;
  let text = "";
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > limit) {
        await reader.cancel();
        throw new Error("Body too large");
      }
      text += decoder.decode(value, { stream: true });
    }
    return text + decoder.decode();
  } finally {
    reader.releaseLock();
  }
}

function json(value: unknown, status = 200) {
  return Response.json(value, {
    status,
    headers: {
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}

export async function proxyQuery(
  request: Request,
  options: {
    apiBase: string;
    appBase?: string;
    cloud: boolean;
    token?: string;
    fetcher?: typeof fetch;
  },
): Promise<Response> {
  if (!sameOrigin(request, options.appBase))
    return json(
      { error: "The request must originate from this application." },
      403,
    );
  if (options.cloud && !options.token)
    return json({ error: "Sign in to query this lab." }, 401);
  if (!request.headers.get("content-type")?.startsWith("application/json"))
    return json({ error: "A JSON request is required." }, 415);
  let payload;
  try {
    payload = querySchema.parse(
      JSON.parse(await readBoundedBody(request.body, MAX_REQUEST_BYTES)),
    );
  } catch {
    return json(
      {
        error:
          "Check the question and calculation fields. Use only synthetic information.",
      },
      400,
    );
  }
  let destination;
  try {
    destination = apiDestination(options.apiBase, options.cloud);
  } catch {
    return json(
      { error: "The API connection is not configured correctly." },
      503,
    );
  }
  try {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (options.cloud && options.token)
      headers.Authorization = `Bearer ${options.token}`;
    const response = await (options.fetcher ?? fetch)(destination, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
      cache: "no-store",
      redirect: "error",
      signal: AbortSignal.timeout(60_000),
    });
    if (!response.ok) {
      const status = [401, 403, 422, 429].includes(response.status)
        ? response.status
        : 502;
      const message =
        status === 401
          ? "Your session has expired. Sign in again."
          : status === 429
            ? "The lab is busy. Try again shortly."
            : status === 422
              ? "The API could not validate the question, company ID, or calculation."
              : "The API could not complete this request. Try again or check the service.";
      return json({ error: message }, status);
    }
    const result = responseSchema.safeParse(
      JSON.parse(await readBoundedBody(response.body, MAX_RESPONSE_BYTES)),
    );
    if (
      !result.success ||
      (payload.company_id && !result.data.human_review_required)
    )
      return json(
        { error: "The API returned an unexpected response format." },
        502,
      );
    return json(result.data);
  } catch {
    return json(
      {
        error:
          "The API is unavailable or timed out. Check that the backend is running, then retry.",
      },
      502,
    );
  }
}
