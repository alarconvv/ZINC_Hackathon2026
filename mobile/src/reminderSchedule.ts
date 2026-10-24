export function reminderSchedule(time: string, trainingDays: string[]) {
  if (!/^([01]\d|2[0-3]):[0-5]\d$/.test(time))
    throw new Error("Choose a time in 24-hour format, such as 09:00.");
  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    [hour, minute] = time.split(":").map(Number);
  return trainingDays.map((day) => {
    const weekday = days.indexOf(day) + 1;
    if (!weekday) throw new Error("Unknown training day. Refresh your plan.");
    return { day, weekday, hour, minute };
  });
}
