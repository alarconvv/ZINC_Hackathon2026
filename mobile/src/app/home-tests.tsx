import { useEffect, useState } from "react";
import { router } from "expo-router";
import { Screen, Title, Card, H, T, Meta, Button, Row } from "../components";
import { useSession } from "../session";
import { elapsedSeconds } from "../timer";
export default function HomeTests() {
  const { data, run, act } = useSession();
  const [kind, setKind] = useState<"chair_stand" | "single_leg_balance">(
      "chair_stand",
    ),
    [start, setStart] = useState<number | null>(null),
    [seconds, setSeconds] = useState(0),
    [count, setCount] = useState(0),
    [running, setRunning] = useState(false),
    [saved, setSaved] = useState(false);
  useEffect(() => {
    if (!running || start === null) return;
    const tick = () => {
      const next = elapsedSeconds(start, Date.now());
      setSeconds(next);
      if (next === 30) setRunning(false);
    };
    const id = setInterval(tick, 100);
    return () => clearInterval(id);
  }, [running, start]);
  return (
    <Screen>
      <Title>Your home tests</Title>
      <Card>
        <H>Record a starting point</H>
        <T>
          These self-reported records do not change your plan. Follow clinician
          guidance, use stable support and do not test if it feels unsafe. Stop
          if you feel unwell.
        </T>
        <Meta>
          Beta — content pending professional review. This is a record, not a
          clinical assessment.
        </Meta>
        <Row>
          <Button
            title="30-second chair stands"
            variant={kind === "chair_stand" ? "primary" : "secondary"}
            disabled={running}
            onPress={() => {
              setKind("chair_stand");
              setStart(null);
              setSeconds(0);
              setCount(0);
              setSaved(false);
            }}
          />
          <Button
            title="Single-leg balance timer"
            variant={kind === "single_leg_balance" ? "primary" : "secondary"}
            disabled={running}
            onPress={() => {
              setKind("single_leg_balance");
              setStart(null);
              setSeconds(0);
              setCount(0);
              setSaved(false);
            }}
          />
        </Row>
        <H>
          {kind === "chair_stand"
            ? `${30 - seconds} seconds remaining · ${count} stands`
            : `${seconds} seconds`}
        </H>
        <Meta>
          Timer uses elapsed time and has no animation. Single-leg balance is
          capped at 30 seconds.
        </Meta>
        <Button
          title="Start home test"
          disabled={running || data?.state.stopped}
          onPress={() => {
            setStart(Date.now());
            setCount(0);
            setSeconds(0);
            setSaved(false);
            setRunning(true);
          }}
        />
        {kind === "chair_stand" ? (
          <Button
            title="Count a chair stand"
            disabled={!running}
            onPress={() => {
              if (start !== null && elapsedSeconds(start, Date.now()) < 30)
                setCount((n) => n + 1);
            }}
          />
        ) : (
          <Button
            title="Stop balance timer"
            variant="secondary"
            disabled={!running}
            onPress={() => {
              if (start !== null) setSeconds(elapsedSeconds(start, Date.now()));
              setRunning(false);
            }}
          />
        )}
        <Button
          title="Save test result"
          disabled={
            start === null ||
            running ||
            saved ||
            (kind === "chair_stand" && seconds !== 30)
          }
          onPress={() =>
            void run(async () => {
              await act("/tests", {
                kind,
                value: kind === "chair_stand" ? count : seconds,
              });
              setSaved(true);
            })
          }
        />
        {saved && (
          <T accessibilityLiveRegion="polite">
            Result saved. Your plan is unchanged.
          </T>
        )}
        <Button
          title="Back to Progress"
          variant="secondary"
          onPress={() => router.replace("/progress")}
        />
      </Card>
    </Screen>
  );
}
