import { TFunction } from "i18next";
import i18next from "i18next";
import axios, { type AxiosError } from "axios";

type DRFError = {
  detail?: string;
  non_field_errors?: string[];
  [key: string]: string | string[] | undefined; // index signature
};

// type guard: unknown -> plain object (record)
function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null;
}

function authErrorMessage(err_loc_code: string, t?: TFunction): string {
  const tf = t ?? i18next.t.bind(i18next);
  return tf(err_loc_code);
}

export function extractApiError(err: unknown, t?: TFunction): { message: string; fields?: Record<string,string[]> } {
  const fallback = { message: authErrorMessage("httpError.fallBack", t) };
  let status: number | undefined;
  let data: unknown;
  // Is Axios error?
  if (axios.isAxiosError<DRFError>(err)) {
    const ax = err as AxiosError<DRFError>;
    status = ax.response?.status;
    data = ax.response?.data;
    // Network/timeout: Axios error without a response object
    if (!ax.response) {
      return { message: authErrorMessage("httpError.networkError", t) };
    }
  } else if (isRecord(err)) {
    // cases: thrown AxiosResponse, or a custom error wrapper
    status = (err as any)?.status ?? (err as any)?.response?.status;
    data =
      (err as any)?.data ??
      (err as any)?.response?.data ??
      (err as any)?.value?.data ??
      (err as any)?.error ??
      err;
  }

  if (!data) return { message: `authErrorMessage("httpError.serverError", t) (${status}).` };
  if (isRecord(data)) {
    // let res_list = []
    const topMsg = data.message;
    console.log("topMsg = ", topMsg)
    console.log("data = ", data)
    if (typeof topMsg === "string") {
      return { message: topMsg };
    }
    const maybeErr = data.error;
    if (isRecord(maybeErr) && typeof maybeErr.message === "string") {
      return { message: maybeErr.message };
    }
  }
  /*
    TODO: add text retrieving for the HTTP error when plain HTML is returned.
    Example (but it returns plain HTML at the moment):
    if (typeof data === "string") {
      return { message: data || (status ? `Server error (${status}).` : fallback.message) };
    }
  */

  // DRF common shapes
  if (isRecord(data)) {
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

    return { message: topMessage || authErrorMessage("httpError.validationError", t), fields: Object.keys(fields).length ? fields : undefined };
  }

  return fallback;
}
