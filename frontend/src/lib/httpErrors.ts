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

function getArrayFromString(stringValue: string, arrayToAppend: Array<string>, indent: string) {
  // Get array from passed string, if present, and append to a collector var.
  const valStr = stringValue as string;
  const looksLikeArray = /^\s*\[.*\]\s*$/.test(valStr);
  if (looksLikeArray) {
    try {
      const parsed = JSON.parse(valStr.replace(/'/g, '"'));
      if (Array.isArray(parsed)) {
        for (const item of parsed) {
          arrayToAppend.push("\n");
          arrayToAppend.push(String(indent + item));
        }
      } else {
        arrayToAppend.push(String(indent + String(parsed)));
      }
    } catch {
      arrayToAppend.push("\n");
      arrayToAppend.push(String(indent + valStr));
    }
  } else {
    arrayToAppend.push("\n");
    arrayToAppend.push(String(indent + valStr));
  }
  return arrayToAppend
} 

export function extractApiError(err: unknown, t?: TFunction): { message: string; fields?: Record<string,string[]> } {
  const fallback = { message: authErrorMessage("httpError.fallBack", t) };
  let status: number | undefined;
  let data: unknown;
  const NBSP = "\u00A0";
  const indent = (n = 4) => NBSP.repeat(n);
  const indent_4 = indent(4) + "-> "
  const indent_8 = indent(8) + "-> "
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

  if (isRecord(data)) {
    // {"message": "A server error occurred.", "detail":"['This password is too common.']"}
    // {"message": "A server error occurred.", "detail":"Cannot delete current user."}
    let mes_det_arr: string[] = [];
    if (typeof (data as any).message === "string") {
      mes_det_arr.push("\n")
      mes_det_arr.push((data as any).message);
    }

    // {"detail":"['This password is too common.']"}
    // {"detail":"Cannot delete current user."}
    let topDetails: unknown = (data as any).detail;
    if (typeof topDetails === "string" && /^\s*\[.*\]\s*$/.test(topDetails)) {
      mes_det_arr = getArrayFromString(topDetails, mes_det_arr, indent_4)
       if (mes_det_arr.length) {
         return { message: mes_det_arr.join(" ") };
       } else {
         return { message: "" };
       }
    } else if (Array.isArray(topDetails)) {
      for (const item of topDetails) {
        mes_det_arr.push("\n")
        mes_det_arr.push(String(indent_4 + item));
      }
      if (mes_det_arr.length) {
        return { message: mes_det_arr.join(" ") };
      } else {
          return { message: "" };
      }
    } else if (topDetails && typeof (topDetails as any) === "string") {
      mes_det_arr.push("\n")
      mes_det_arr.push(String(indent_4 + topDetails));
      if (mes_det_arr.length) {
        return { message: mes_det_arr.join(" ") };
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

    let err_mes_det_arr: string[] = [];
    const errorObj = isRecord((data as any).error) ? (data as any).error : null;
    if (errorObj && typeof (errorObj as any).message === "string") {
      err_mes_det_arr.push("\n")
      err_mes_det_arr.push((errorObj as any).message);
    }

    const details = errorObj ? (errorObj as any).details : undefined;
    if (details !== undefined && details !== null) {
      if (isRecord(details)) {
        for (const val of Object.values(details)) {
          err_mes_det_arr.push("\n")
          err_mes_det_arr.push(String(indent_4 + details[val]));
          if (Array.isArray(val)) {
            for (const item of val) {
              err_mes_det_arr = getArrayFromString(String(item), err_mes_det_arr, indent_8)
            }
          }
          else {
            err_mes_det_arr = getArrayFromString(String(val), err_mes_det_arr, indent_8)
          }
        }
      } else if (Array.isArray(details)) {
        for (const item of details) {
          err_mes_det_arr.push("\n")
          err_mes_det_arr.push(String(indent_8 + item));
        }
      } else if (details && typeof (details as any) === "string") {
        err_mes_det_arr.push("\n")
        err_mes_det_arr.push(String(indent_8 + details));
      }
    }
    if (err_mes_det_arr.length) {
      return { message: err_mes_det_arr.join(" ") };
    } else {
      return { message: "" };
    }
  }

  // Common shapes
  if (isRecord(data)) {
    const fields: Record<string, string[]> = {};

    // detail
    if ("detail" in data && typeof data.detail === "string") {
      const det = (data as any).detail;
      if (typeof det === "string") {
        return { message: det };
      }
      if (Array.isArray(det)) {
        return { message: det.map(String).join(" ") };
      }
    }
    // collect field errors & non_field_errors
    let topMessage = "";
    for (const [key, value] of Object.entries(data)) {
      if (Array.isArray(value)) {
        fields[key] = value.map(String);
      } else if (typeof value === "string") {
        fields[key] = [value];
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
