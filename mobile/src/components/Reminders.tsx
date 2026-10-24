import { useEffect, useState } from "react";
import { Platform } from "react-native";
import { Card, H, T, Meta, Input, Button } from "./index";
import { useSession } from "../session";
import {
  enableReminders,
  disableReminders,
  reminderPreference,
} from "../reminders";
export default function Reminders() {
  const { data, run } = useSession();
  const [time, setTime] = useState("09:00"),
    [enabled, setEnabled] = useState(false);
  useEffect(() => {
    reminderPreference()
      .then((p) => {
        if (p && p.owner === data?.user?.email) {
          setEnabled(true);
          setTime(p.time);
        }
      })
      .catch(() => {});
  }, [data?.user?.email]);
  if (Platform.OS === "web" || !data?.state.plan || data.state.stopped)
    return null;
  return (
    <Card>
      <H>Your training reminders</H>
      <T>
        Local reminders on {data.state.plan.days.join(", ")}. Nothing is sent to
        a notification server.
      </T>
      <Input
        label="Reminder time (HH:MM)"
        value={time}
        onChangeText={setTime}
      />
      <Button
        title={enabled ? "Update reminders" : "Enable reminders"}
        onPress={() =>
          void run(async () => {
            await enableReminders(
              data.user!.email,
              time,
              data.state.plan!.days,
            );
            setEnabled(true);
          })
        }
      />
      {enabled && (
        <Button
          title="Turn off reminders"
          variant="secondary"
          onPress={() =>
            void run(async () => {
              await disableReminders();
              setEnabled(false);
            })
          }
        />
      )}
      <Meta>
        Permission is requested only when you enable reminders. Your device
        controls delivery. Reminders stop after sign-out or Stop and follow
        schedule changes when you open ZINC.
      </Meta>
    </Card>
  );
}
