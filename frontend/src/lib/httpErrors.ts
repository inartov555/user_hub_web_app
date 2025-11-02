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

  if (!data) {
    return {
      message:
        authErrorMessage("httpError.serverError", t) +
        (status ? ` (${status}).` : ""),
    };
  }

  // {"message": "A server error occurred.", "detail":"['This password is too common.']"}
  // {"message": "A server error occurred.", "detail":"Cannot delete current user."}
  if (isRecord(data)) {
    const collected: string[] = ["\n"];
    if (typeof (data as any).message === "string") {
      collected.push((data as any).message);
    }

    // {"detail":"['This password is too common.']"}
    // {"detail":"Cannot delete current user."}
    let topDetails: unknown = (data as any).detail;
    if (typeof topDetails === "string" && /^\s*\[.*\]\s*$/.test(topDetails)) {
      collected.push("\n") // after message text
      const parsed = JSON.parse(topDetails.replace(/'/g, '"'));
      if (Array.isArray(parsed)) {
          for (const item of parsed) {
            collected.push(String("\t" + item));
          }
       } else {
          collected.push(String("\t" + parsed));
       }
       if (collected.length) {
         return { message: collected.join(" ") };
       } else {
         return { message: "" };
       }
    } else if (Array.isArray(topDetails)) {
      for (const item of topDetails) {
        collected.push(String("\t" + item));
      }
      if (collected.length) {
        return { message: collected.join(" ") };
      } else {
          return { message: "" };
      }
    } else if (topDetails && typeof (topDetails as any) === "string") {
      collected.push(String("\t" + topDetails));
      if (collected.length) {
        return { message: collected.join(" ") };
      } else {
          return { message: "" };
      }
    }

    /*
       Example:

       {
         "error": {
           "code": "common.server_error",
           "message": "A server error occurred.",
           "i18n_key": "errors.common.server_error",
           "details": {
             "password": [
               "The password is too similar to the username.",
               "This password is too short. It must contain at least 8 characters.",
               "This password is too common."
             ]
           },
           "lang": "en-us"
         }
       }
     */

    // Replace the invalid maybeErr/res_list block with this collector
    const errorObj = isRecord((data as any).error) ? (data as any).error : null;
    if (errorObj && typeof (errorObj as any).message === "string") {
      collected.push((errorObj as any).message);
    }

    const details = errorObj ? (errorObj as any).details : undefined;
    if (details !== undefined) {
      collected.push("\n") // after message text
      if (isRecord(details)) {
        for (const v of Object.values(details)) {
          if (Array.isArray(v)) {
            for (const item of v) {
              collected.push(String("\t" + item));
              collected.push("\n")
            }
          }
          else if (topDetails && typeof (topDetails as any) === "string") {
            collected.push(String("\t" + v));
            collected.push("\n")
          }
        }
      } else if (Array.isArray(details)) {
        for (const item of details) {
          collected.push(String("\t" + item));
          collected.push("\n")
        }
      } else if (topDetails && typeof (topDetails as any) === "string") {
        collected.push(String("\t" + details));
        collected.push("\n")
      }
    }
    if (collected.length) {
      return { message: collected.join(" ") };
    } else {
      return { message: "" };
    }
  }

  // Common shapes
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
