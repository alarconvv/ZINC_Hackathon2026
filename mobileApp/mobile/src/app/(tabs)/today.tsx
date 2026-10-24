import { View, useWindowDimensions } from "react-native";
import { useState } from "react";
import { router } from "expo-router";
import {
  Screen,
  Title,
  Card,
  H,
  T,
  Meta,
  Button,
  Row,
  Ring,
  Sheet,
} from "../../components";
import { useSession } from "../../session";
import { labels } from "../../types";
export default function Today() {
  const phone = useWindowDimensions().width < 600;
  const { data, run, act, busy, error } = useSession();
  const [weekReady, setWeekReady] = useState("");
  const [confirmWeek, setConfirmWeek] = useState(false);
  const view = data?.view,
    plan = data?.state.plan;
  if (!plan || !view) return null;
  const action = view.today_action;
  const next = action.activity;
  const upcoming = view.next_activity;
  return (
    <Screen>
      <Title>Your day, {data.state.profile.name}.</Title>
      <Meta light>
        {plan.tier} · Week {plan.week} · Beginning {plan.start_date}
      </Meta>
      {!data.state.tour_done && (
        <Card>
          <H>How ZINC works</H>
          <T>1. Week — your dated activities.</T>
          <T>2. Train — log each set, effort and pain.</T>
          <T>
            3. Coach — review your week and accept or decline next week’s goal.
          </T>
          <Button
            title="Got it"
            variant="secondary"
            onPress={() => {
              void run(async () => {
                await act("/guide/dismiss");
              });
            }}
          />
        </Card>
      )}
      <Card>
        <H>
          {action.kind === "resume"
            ? "Continue where you left off"
            : action.kind === "start"
              ? "Your next step today"
              : action.kind === "recover"
                ? "Make room for a fresh start"
                : action.kind === "rest"
                  ? "You’re done for today"
                  : action.kind === "empty"
                    ? "Choose your next activity"
                    : "Your week is recorded"}
        </H>
        {next ? (
          <>
            <T>
              {labels[next.section]} · {next.date} · {next.minutes} min
              estimated
            </T>
            <Button
              title={
                action.kind === "resume"
                  ? "Resume activity"
                  : "Start today’s activity"
              }
              busy={busy}
              onPress={() =>
                void run(async () => {
                  await act(`/activities/${next.id}/start`);
                  router.push("/train");
                })
              }
            />
          </>
        ) : (
          <T>
            {action.kind === "recover"
              ? `${view.missed_count} missed ${view.missed_count === 1 ? "activity" : "activities"}. Reschedule or skip what no longer fits; there’s no need to catch up all at once.`
              : action.kind === "rest"
                ? `Enjoy the space in your day. Next on your schedule: ${upcoming ? `${labels[upcoming.section]} on ${upcoming.date}` : "your next week"}.`
                : action.kind === "empty"
                  ? "Add an activity from Week when you’re ready. Your recommended routine is still available there."
                  : "Review what you recorded on Progress."}
          </T>
        )}
        <Button
          title={
            action.kind === "recover"
              ? "Review missed activities"
              : "Explore my week"
          }
          variant={next ? "secondary" : "primary"}
          onPress={() => router.push("/week")}
        />
      </Card>
      <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 12 }}>
        {view.sections.map((s) => (
          <View
            key={s.id}
            style={{ flexGrow: 1, flexBasis: phone ? "47%" : 210 }}
          >
            <Card compact={phone}>
              <Row>
                <View style={{ flex: 1 }}>
                  <T
                    accessibilityRole="header"
                    style={{
                      fontFamily: "DMSans_600SemiBold",
                      fontSize: phone ? 16 : 22,
                      lineHeight: phone ? 23 : 30,
                    }}
                  >
                    {s.name}
                  </T>
                </View>
                <Ring
                  size={phone ? 44 : 68}
                  percent={s.total ? (100 * s.done) / s.total : 0}
                  label={`${s.done}/${s.total}`}
                />
              </Row>
              <Meta>
                {!s.total
                  ? "Not scheduled"
                  : s.next_date
                    ? `${s.next_date < view.today ? "Missed" : "Next"}: ${s.next_date}`
                    : s.done === s.total
                      ? "All done"
                      : "No activities remaining"}
              </Meta>
            </Card>
          </View>
        ))}
      </View>
      <Card>
        <H>A fresh week, when you’re ready</H>
        <T>Review your feedback with Coach. Accepted goals begin next week.</T>
        <Meta>
          Next: Week {view.next_week.week} · {view.next_week.start_date} to{" "}
          {view.next_week.end_date}
        </Meta>
        {error ? <T accessibilityRole="alert">{error}</T> : null}
        {weekReady ? <T accessibilityLiveRegion="polite">{weekReady}</T> : null}
        <Button
          title="Start next week"
          variant="secondary"
          busy={busy}
          onPress={() => setConfirmWeek(true)}
        />
      </Card>
      <Sheet
        title="Review your next week"
        visible={confirmWeek}
        onClose={() => setConfirmWeek(false)}
      >
        <H>Week {view.next_week.week}</H>
        <T>
          {view.next_week.start_date} to {view.next_week.end_date}
        </T>
        <T>
          Your current week will be saved in Progress. Your chosen schedule
          carries forward; accepted goals begin in the new week.
        </T>
        {view.next_week.unstarted_count > 0 && (
          <T>
            {view.next_week.unstarted_count} activities haven’t been started.
            They will remain uncompleted in this week’s history. You can return
            to Week to reschedule or skip them first.
          </T>
        )}
        {view.next_week.unfinished_count > 0 && (
          <T>
            Finish or skip your in-progress activities before starting a new
            week.
          </T>
        )}
        <Button
          title={`Start week ${view.next_week.week}`}
          disabled={view.next_week.unfinished_count > 0}
          busy={busy}
          onPress={() =>
            void run(async () => {
              setWeekReady("");
              const result = await act("/week/next");
              setConfirmWeek(false);
              setWeekReady(
                `Week ${result.state.plan!.week} is ready, beginning ${result.state.plan!.start_date}. Open “Explore my week” to see your activities.`,
              );
            })
          }
        />
        <Button
          title="Keep working on this week"
          variant="secondary"
          onPress={() => setConfirmWeek(false)}
        />
        {error ? <T accessibilityRole="alert">{error}</T> : null}
      </Sheet>
    </Screen>
  );
}
