import fs from "node:fs";
import path from "node:path";
import base from "./app.json";
export default {
  ...base.expo,
  extra: {
    privacy: fs.readFileSync(
      path.join(__dirname, "content/privacy.md"),
      "utf8",
    ),
    terms: fs.readFileSync(path.join(__dirname, "content/terms.md"), "utf8"),
    apiUrl: process.env.EXPO_PUBLIC_API_URL || "http://127.0.0.1:8000",
  },
};
