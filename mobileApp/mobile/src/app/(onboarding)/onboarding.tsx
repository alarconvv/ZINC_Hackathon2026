import { useEffect, useState } from "react";
import { router } from "expo-router";
import { View } from "react-native";
import {
  Screen,
  Title,
  Card,
  H,
  T,
  Meta,
  Input,
  Check,
  Row,
  Button,
  Chip,
} from "../../components";
import { useSession } from "../../session";
import { request } from "../../api";
import { labels, Section, Snapshot } from "../../types";
const weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
export default function Onboarding() {
  const { data, token, run, act, busy, error } = useSession();
  const p = data?.state.profile;
  const [phase, setPhase] = useState(
      data?.state.safety_result ? "result" : "profile",
    ),
    [name, setName] = useState(p?.name || ""),
    [age, setAge] = useState(String(p?.age || 52)),
    [level, setLevel] = useState(p?.level || "beginner"),
    [limits, setLimits] = useState<string[]>(p?.limits || []),
    [mci, setMci] = useState(p?.mci || false),
    [clearance, setClearance] = useState(p?.clinician_clearance || false);
  const [questions, setQuestions] = useState<Record<string, string>>({}),
    [q, setQ] = useState(0),
    [answers, setAnswers] = useState<Record<string, boolean>>({}),
    [result, setResult] = useState(""),
    [monday, setMonday] = useState(""),
    [extraYoga, setExtraYoga] = useState(false),
    [extraBrain, setExtraBrain] = useState(false),
    [suggested, setSuggested] = useState<Record<Section, number[]> | null>(
      null,
    ),
    [days, setDays] = useState<Record<Section, number[]>>({
      strength: [],
      yoga: [1, 5],
      brain: [1, 5],
      relaxation: [1, 5],
    });
  useEffect(() => {
    if (token)
      request<{ questions: Record<string, string> }>("/safety/questions", token)
        .then((r) => setQuestions(r.questions))
        .catch(() => {});
  }, [token]);
  const keys = Object.keys(questions),
    key = keys[q];
  async function answer(value: boolean) {
    const next = { ...answers, [key]: value };
    setAnswers(next);
    if (q < keys.length - 1) setQ(q + 1);
    else {
      await run(async () => {
        const r = await act<Snapshot & { message: string }>("/safety", {
          answers: next,
        });
        setResult(r.message);
        setPhase("result");
      });
    }
  }
  return (
    <Screen>
      <Title>
        {phase === "profile"
          ? "A week that fits you"
          : phase === "safety"
            ? "Before you begin"
            : phase === "result"
              ? "Your starting point"
              : "Choose your days"}
      </Title>
      <Card>
        {phase === "profile" ? (
          <>
            <Input label="First name" value={name} onChangeText={setName} />
            <Input
              label="Age"
              value={age}
              onChangeText={setAge}
              keyboardType="number-pad"
            />
            <T>Current activity level</T>
            <Row>
              {["beginner", "active", "trained"].map((v) => (
                <Button
                  key={v}
                  title={v}
                  variant={level === v ? "primary" : "secondary"}
                  onPress={() => setLevel(v)}
                />
              ))}
            </Row>
            <T>Limitations to consider</T>
            {["knees", "back", "balance"].map((v) => (
              <Check
                key={v}
                label={v}
                value={limits.includes(v)}
                onChange={(checked) =>
                  setLimits(
                    checked ? [...limits, v] : limits.filter((x) => x !== v),
                  )
                }
              />
            ))}
            <Check
              label="A clinician has identified mild cognitive impairment"
              value={mci}
              onChange={setMci}
            />
            <Check
              label="I have clinician sign-off for supported exercise (required for age 80+ or mild cognitive impairment)"
              value={clearance}
              onChange={setClearance}
            />
            <Button
              title="Continue to safety"
              busy={busy}
              onPress={() =>
                void run(async () => {
                  await act(
                    "/profile",
                    {
                      name,
                      age: Number(age),
                      level,
                      limits,
                      mci,
                      clinician_clearance: clearance,
                    },
                    "PUT",
                  );
                  setPhase("safety");
                })
              }
            />
          </>
        ) : phase === "safety" ? (
          <>
            <Meta>
              Question {q + 1} of {keys.length}
            </Meta>
            <View
              accessibilityRole="progressbar"
              accessibilityValue={{ min: 0, max: keys.length, now: q + 1 }}
              style={{ height: 6, backgroundColor: "#d6e7f5", borderRadius: 3 }}
            >
              <View
                style={{
                  height: 6,
                  width: `${((q + 1) / Math.max(1, keys.length)) * 100}%`,
                  backgroundColor: "#126bc5",
                }}
              />
            </View>
            <H>{questions[key] || "Loading safety questions…"}</H>
            <Meta>
              This shortened screen is not the full PAR-Q+. Content pending
              professional review. Follow clinician guidance and stop if you
              feel unwell.
            </Meta>
            <Row>
              <Button
                title="Yes"
                disabled={!key}
                onPress={() => void answer(true)}
              />
              <Button
                title="No"
                disabled={!key}
                onPress={() => void answer(false)}
              />
            </Row>
            {q > 0 && (
              <Button
                title="Previous question"
                variant="secondary"
                onPress={() => setQ(q - 1)}
              />
            )}
            <Button
              title="Back to profile"
              variant="secondary"
              onPress={() => setPhase("profile")}
            />
          </>
        ) : phase === "result" ? (
          <>
            <H>
              {result ||
                (data?.state.safety_result === "clinician"
                  ? "Please see a clinician before starting."
                  : "You're cleared to start")}
            </H>
            <T>
              Based on this shortened screen. Follow any clinician guidance and
              stop if you feel unwell.
            </T>
            {data?.state.safety_result === "clinician" ? (
              <Button
                title="Back to profile"
                onPress={() => setPhase("profile")}
              />
            ) : (
              <Button
                title="See my suggested week"
                busy={busy}
                onPress={() =>
                  void run(async () => {
                    const result = await request<{
                      choices: Record<Section, number[]>;
                      start_date: string;
                    }>("/plan/suggestion", token);
                    setDays(result.choices);
                    setSuggested(result.choices);
                    setMonday(result.start_date);
                    setPhase("days");
                  })
                }
              />
            )}
          </>
        ) : (
          <>
            <T>
              We’ve suggested days for your recommended activities. Keep them or
              choose days that fit your life. Leave a rest day between strength
              sessions, including Sunday and Monday.
            </T>
            <H>Your week at a glance</H>
            {weekdays.map((day, i) => (
              <T key={day}>
                {day} ·{" "}
                {(Object.keys(labels) as Section[])
                  .filter((s) => days[s].includes(i))
                  .map((s) => labels[s])
                  .join(", ") || "Rest day"}
              </T>
            ))}
            <H>Change your days</H>
            <Input
              label="Start Monday (YYYY-MM-DD, optional)"
              value={monday}
              onChangeText={setMonday}
              placeholder="Use this week's Monday"
            />
            {(Object.keys(labels) as Section[]).map((section) => (
              <View key={section} style={{ gap: 8 }}>
                <H>{labels[section]}</H>
                <Meta>
                  Recommended: {suggested?.[section].length ?? 2} days per week
                </Meta>
                <Row>
                  {weekdays.map((day, i) => (
                    <Button
                      key={day}
                      title={`${section} ${day}`}
                      variant={
                        days[section].includes(i) ? "primary" : "secondary"
                      }
                      onPress={() =>
                        setDays({
                          ...days,
                          [section]: days[section].includes(i)
                            ? days[section].filter((d) => d !== i)
                            : [...days[section], i],
                        })
                      }
                    />
                  ))}
                </Row>
                <Chip label={days[section].length + " days selected"} />
              </View>
            ))}
            <Meta>
              Start with the recommended week. After creating it, use Week to
              reschedule, skip or remove activities. Removed activities can be
              added again.
            </Meta>
            <H>Optional extras</H>
            <Meta>
              These add Sunday sessions to your week. They aren’t required, and
              you can also add activities later.
            </Meta>
            <Check
              label="Extra yoga"
              value={extraYoga}
              onChange={setExtraYoga}
            />
            <Check
              label="Extra brain games and relaxation"
              value={extraBrain}
              onChange={setExtraBrain}
            />
            <Meta>
              Extra yoga adds a short stretching session. Extra brain games and
              relaxation add a reasoning game and a breathing session.
            </Meta>
            <Button
              title="Create my week"
              busy={busy}
              onPress={() =>
                void run(async () => {
                  await act("/plan", {
                    ...(monday ? { start_date: monday } : {}),
                    choices: days,
                    toggles: { yoga: extraYoga, brain: extraBrain },
                  });
                  router.replace("/today");
                })
              }
            />
            {error ? <T accessibilityRole="alert">{error}</T> : null}
          </>
        )}
      </Card>
    </Screen>
  );
}
