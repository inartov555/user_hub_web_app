import axios, { type AxiosError } from "axios";

type DRFError = {
  detail?: string;
  non_field_errors?: string[];
  [key: string]: string | string[] | undefined; // index signature
};

export function extractApiError(err: unknown): { message: string; fields?: Record<string,string[]> } {
  const fallback = { message: "Request failed. Please try again." };
  let status: number | undefined;
  let data: unknown;
  // Is Axios error?
  if (axios.isAxiosError<DRFError>(err)) {
    const ax = err as AxiosError<DRFError>;
    status = ax.response?.status;
    data = ax.response?.data;
    // Network/timeout: Axios error without a response object
    if (!ax.response) {
      return { message: "Network error. Check your connection and try again." };
    }
  } else if (typeof err === "object" && err !== null) {
    const anyErr = err as any;
    // cases: thrown AxiosResponse, or a custom error wrapper
    status = anyErr?.status ?? anyErr?.response?.status;
    data = anyErr?.data ?? anyErr?.response?.data ?? anyErr?.value?.data ?? anyErr;
  }

  if (!data) return { message: `Server error (${status}).` };
  /*
    TODO: add text retrieving for the HTTP error when plain HTML is returned.
    Example (but it returns plain HTML at the moment):
    if (typeof data === "string") {
      return { message: data || (status ? `Server error (${status}).` : fallback.message) };
    }
  */

  // DRF common shapes
  if (typeof data === "object" && data !== null) {
    const fields: Record<string, string[]> = {};

    // detail
    if ("detail" in data && typeof data.detail === "string") {
      const d = (data as any).detail;
      if (typeof d === "string") {
        return { message: d };
      }
      if (Array.isArray(d)) {
        return { message: d.map(String).join(" ") };
      }
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
