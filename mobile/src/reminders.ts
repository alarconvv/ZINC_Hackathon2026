import { reminderSchedule } from "./reminderSchedule";
import { Platform } from "react-native";
import * as SecureStore from "expo-secure-store";
const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
type Preference = { owner: string; time: string };
let queue = Promise.resolve();
async function cancel() {
  if (Platform.OS === "web") return;
  const n = await import("expo-notifications");
  for (const day of days)
    await n.cancelScheduledNotificationAsync("zinc-strength-" + day);
}
export async function reminderPreference(): Promise<Preference | null> {
  if (Platform.OS === "web") return null;
  const raw = await SecureStore.getItemAsync("zinc-reminders");
  return raw ? JSON.parse(raw) : null;
}
export function syncReminders(
  owner?: string,
  trainingDays: string[] = [],
  stopped = false,
) {
  queue = queue
    .catch(() => {})
    .then(async () => {
      if (Platform.OS === "web") return;
      await cancel();
      const preference = await reminderPreference();
      if (!preference || !owner || preference.owner !== owner || stopped)
        return;
      const n = await import("expo-notifications");
      if (!(await n.getPermissionsAsync()).granted) return;
      for (const { day, weekday, hour, minute } of reminderSchedule(
        preference.time,
        trainingDays,
      ))
        await n.scheduleNotificationAsync({
          identifier: "zinc-strength-" + day,
          content: { title: "ZINC", body: "Your strength session is today." },
          trigger: {
            type: n.SchedulableTriggerInputTypes.WEEKLY,
            weekday,
            hour,
            minute,
            channelId: "zinc-training",
          },
        });
    });
  return queue;
}
export async function enableReminders(
  owner: string,
  time: string,
  trainingDays: string[],
) {
  reminderSchedule(time, trainingDays);
  if (Platform.OS === "web") return;
  const n = await import("expo-notifications");
  if (Platform.OS === "android")
    await n.setNotificationChannelAsync("zinc-training", {
      name: "Training reminders",
      importance: n.AndroidImportance.DEFAULT,
    });
  if (!(await n.requestPermissionsAsync()).granted)
    throw new Error(
      "Reminders need notification permission. You can allow it in your device settings.",
    );
  await SecureStore.setItemAsync(
    "zinc-reminders",
    JSON.stringify({ owner, time }),
  );
  await syncReminders(owner, trainingDays);
}
export async function disableReminders() {
  if (Platform.OS === "web") return;
  await SecureStore.deleteItemAsync("zinc-reminders");
  await syncReminders();
}
