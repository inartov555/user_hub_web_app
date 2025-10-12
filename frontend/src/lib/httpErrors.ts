import type { AxiosError } from "axios";

type DRFError =
  | { detail?: string; non_field_errors?: string[] }
  | Record<string, string[] | string>;

export function extractApiError(err: unknown): { message: string; fields?: Record<string,string[]> } {
  const fallback = { message: "Request failed. Please try again." };

  // Axios error?
  const ax = err as AxiosError<DRFError>;
  if (!ax || !ax.isAxiosError) return fallback;

  // Network/timeout
  if (!ax.response) {
    return { message: "Network error. Check your connection and try again." };
  }

  const { status, data } = ax.response;
  if (!data) return { message: `Server error (${status}).` };

  // DRF common shapes
  if (typeof data === "object") {
    const fields: Record<string, string[]> = {};

    // detail
    if ("detail" in data && typeof data.detail === "string") {
      return { message: data.detail };
    }

    // collect field errors & non_field_errors
    let topMessage = "";
    for (const [k, v] of Object.entries(data)) {
      if (Array.isArray(v)) {
        fields[k] = v.map(String);
      } else if (typeof v === "string") {
        fields[k] = [v];
      }
    }

    // Prefer non_field_errors as top-level
    if (fields.non_field_errors?.length) {
      topMessage = fields.non_field_errors.join(" ");
    } else if (fields.__all__?.length) {
      topMessage = fields.__all__.join(" ");
    } else if (fields.username?.length) {
      topMessage = fields.username.join(" ");
    } else if (fields.email?.length) {
      topMessage = fields.email.join(" ");
    }

    return { message: topMessage || "Validation error.", fields: Object.keys(fields).length ? fields : undefined };
  }

  return fallback;
}
