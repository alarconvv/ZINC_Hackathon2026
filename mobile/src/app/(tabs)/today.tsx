import { View, useWindowDimensions } from "react-native";
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
} from "../../components";
import { useSession } from "../../session";
import { labels } from "../../types";
export default function Today() {
  const phone = useWindowDimensions().width < 600;
  const { data, run, act, busy } = useSession();
  const view = data?.view,
    plan = data?.state.plan;
  if (!plan || !view) return null;
  const next = view.next_activity;
  return (
    <Screen>
      <Title>Your complete week, {data.state.profile.name}.</Title>
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
                {s.next_date
                  ? `Next: ${s.next_date}`
                  : s.done === s.total
                    ? "All done"
                    : "No activities remaining"}
              </Meta>
            </Card>
          </View>
        ))}
      </View>
      <Card>
        <H>{next ? "Your next activity" : "Your week is recorded"}</H>
        {next ? (
          <>
            <T>
              {labels[next.section]} · {next.date} · {next.minutes} min
              estimated
            </T>
            <Button
              title={
                next.status === "partial"
                  ? "Resume next activity"
                  : "Start next activity"
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
          <T>Review what you recorded on Progress.</T>
        )}
        <Button
          title="Explore my week"
          variant="secondary"
          onPress={() => router.push("/week")}
        />
      </Card>
      <Card>
        <H>A fresh week, when you’re ready</H>
        <T>Review your feedback with Coach. Accepted goals begin next week.</T>
        <Button
          title="Start next week"
          variant="secondary"
          onPress={() =>
            void run(async () => {
              await act("/week/next");
            })
          }
        />
      </Card>
    </Screen>
  );
}
