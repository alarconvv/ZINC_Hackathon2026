
import base from "./app.json";

export default {
  ...base.expo,
  plugins: [
    ...(base.expo.plugins || []),
    "expo-video",
  ],
  extra: {
    apiUrl: process.env.EXPO_PUBLIC_API_URL || "http://127.0.0.1:8000",
  },
};
