import { useState } from "react";
import { View } from "react-native";
import { router } from "expo-router";
import {
  Screen,
  Title,
  Card,
  H,
  T,
  Meta,
  Button,
  Chip,
  EvidenceBadge,
  Row,
  Sheet,
  IconButton,
} from "../../components";
import { useSession } from "../../session";
import { Activity, labels, Section } from "../../types";
const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
export default function Week() {
  const { data, run, act, busy, error, clearError } = useSession();
  const [edit, setEdit] = useState<Activity | null>(null),
    [add, setAdd] = useState(false),
    [day, setDay] = useState(0),
    [section, setSection] = useState<Section>("yoga"),
    [confirm, setConfirm] = useState<"remove" | "skip" | null>(null),
    [notice, setNotice] = useState("");
  const rows = data?.view?.activities || [];
  async function save(remove = false) {
    await act("/schedule", {
      ...(edit ? { activity_id: edit.id } : { section }),
      day,
      remove,
    });
    setEdit(null);
    setAdd(false);
    setConfirm(null);
    setNotice(
      remove
        ? "Activity removed. You can add it again with Add activity."
        : "Your schedule is saved.",
    );
  }
  return (
    <Screen>
      <Title>Your week</Title>
      <Meta light>
        Make the week fit your life. Reschedule a missed activity or skip it;
        you don’t need to catch up all at once. Schedule changes carry into next
        week. Recorded activities keep their dates.
      </Meta>
      {notice ? (
        <T style={{ color: "white" }} accessibilityLiveRegion="polite">
          {notice}
        </T>
      ) : null}
      <Card>
        <H>Your recommended week</H>
        {data?.view?.recommendations.map((r) => (
          <T key={r.section}>
            {labels[r.section]}: {r.scheduled} scheduled · {r.recommended}{" "}
            recommended
          </T>
        ))}
        {data?.view?.recommendations.some(
          (r) => r.scheduled < r.recommended,
        ) && (
          <Meta>
            Your schedule has fewer activities than recommended. Add one back
            when it works for you. Completion percentages describe your chosen
            schedule.
          </Meta>
        )}
      </Card>
      <Button
        title="Add activity"
        variant="secondary"
        onPress={() => {
          clearError();
          setConfirm(null);
          setAdd(true);
        }}
      />
      {!rows.length && (
        <T style={{ color: "white" }}>
          Your week has no scheduled activities. Add an activity when you’re
          ready.
        </T>
      )}
      {rows.map((a) => (
        <Card key={a.id} testID={`activity-${a.section}-${a.date}`}>
          <Row>
            <View style={{ width: 52 }}>
              <Meta>
                {new Date(a.date + "T12:00:00").toLocaleDateString("en", {
                  weekday: "short",
                })}
              </Meta>
              <H>{a.date.slice(-2)}</H>
            </View>
            <View style={{ flex: 1, minWidth: 130, gap: 8 }}>
              <H>{labels[a.section]}</H>
              <Row>
                <Chip
                  label={
                    a.status === "completed"
                      ? "Done"
                      : a.status === "partial"
                        ? "In progress"
                        : a.status === "skipped"
                          ? "Skipped"
                          : "Not started"
                  }
                />
                <EvidenceBadge
                  level={
                    a.section === "strength"
                      ? "Strong"
                      : a.section === "brain"
                        ? "Emerging"
                        : "Moderate"
                  }
                />
                <Meta>{a.minutes} min</Meta>
                {a.optional && <Chip label="Extra" />}
                {!a.finished && a.date < (data?.view?.today || "") && (
                  <Chip label="Missed day · choose what’s next" />
                )}
              </Row>
            </View>
            <IconButton
              name="more-horizontal"
              label={`Manage ${labels[a.section]} ${a.date}`}
              onPress={() => {
                clearError();
                setConfirm(null);
                setEdit(a);
                setDay(
                  days.indexOf(
                    new Date(a.date + "T12:00:00").toLocaleDateString("en", {
                      weekday: "short",
                    }),
                  ),
                );
              }}
            />
          </Row>
          <Button
            title={
              a.finished
                ? "Review activity"
                : a.status === "partial"
                  ? "Resume activity"
                  : "Start activity"
            }
            busy={busy}
            onPress={() =>
              void run(async () => {
                await act(`/activities/${a.id}/start`);
                router.push("/train");
              })
            }
          />
        </Card>
      ))}
      <Sheet
        title={
          confirm === "remove"
            ? "Remove this activity?"
            : confirm === "skip"
              ? "Skip this activity?"
              : edit
                ? "Manage activity"
                : "Add activity"
        }
        visible={!!edit || add}
        onClose={() => {
          setEdit(null);
          setAdd(false);
          setConfirm(null);
        }}
      >
        {confirm && edit ? (
          <>
            <H>
              {labels[edit.section]} · {edit.date}
            </H>
            <T>
              {confirm === "remove"
                ? "We recommend keeping your weekly activities for a balanced routine. If this day doesn’t work, try rescheduling first. Removing it also changes future weeks; you can add it again later."
                : "It’s okay to miss a day. This activity will be marked skipped, or partial if you already recorded work. Your results stay saved, and next week’s schedule stays the same."}
            </T>
            <Button
              title={
                confirm === "remove"
                  ? "Remove from my schedule"
                  : "Skip for this week"
              }
              variant="danger"
              busy={busy}
              onPress={() =>
                void run(async () => {
                  if (confirm === "remove") await save(true);
                  else {
                    await act(`/activities/${edit.id}/skip`);
                    setEdit(null);
                    setConfirm(null);
                    setNotice(
                      "Activity ended for this week. Your recorded work is saved. Continue when you’re ready.",
                    );
                  }
                })
              }
            />
            <Button
              title="Keep activity"
              variant="secondary"
              onPress={() => setConfirm(null)}
            />
          </>
        ) : (
          <>
            {!edit && (
              <Row>
                {(Object.keys(labels) as Section[]).map((v) => (
                  <Button
                    key={v}
                    title={labels[v]}
                    variant={section === v ? "primary" : "secondary"}
                    onPress={() => setSection(v)}
                  />
                ))}
              </Row>
            )}
            {!edit?.finished && (
              <>
                <T>Choose a day</T>
                <Row>
                  {days.map((d, i) => (
                    <Button
                      key={d}
                      title={d}
                      variant={day === i ? "primary" : "secondary"}
                      onPress={() => setDay(i)}
                    />
                  ))}
                </Row>
                <Button
                  title="Save activity day"
                  onPress={() => void run(() => save())}
                />
              </>
            )}
            {edit && edit.status === "not started" && (
              <Button
                title="Remove activity"
                variant="danger"
                onPress={() => setConfirm("remove")}
              />
            )}
            {edit && !edit.finished && (
              <Button
                title="Skip activity"
                variant="secondary"
                onPress={() => setConfirm("skip")}
              />
            )}
            <Meta>
              Keep a rest day between strength sessions. Started activities can
              be skipped; their records cannot be removed. Finished activities
              stay on their recorded day.
            </Meta>
          </>
        )}
        {error ? <T accessibilityRole="alert">{error}</T> : null}
      </Sheet>
    </Screen>
  );
}
