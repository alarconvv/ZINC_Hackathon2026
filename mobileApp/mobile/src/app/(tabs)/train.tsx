
import { useState } from "react";
import { View, useWindowDimensions } from "react-native";
import { Feather } from "@expo/vector-icons";
import { router } from "expo-router";

import ExerciseVideo from "../../components/ExerciseVideo";

import {
  Screen,
  Title,
  Card,
  H,
  T,
  Meta,
  Button,
  Input,
  Stepper,
  EvidenceBadge,
  Chip,
  Row,
  Sheet,
} from "../../components";

import { RestTimer, Breathing } from "../../components/Timers";
import { useSession } from "../../session";
import { API_URL } from "../../api";
import { labels } from "../../types";

export default function Train() {
  const { data } = useSession();
  const a = data?.view?.active;

  return (
    <TrainSession
      key={[a?.id, a?.item?.id, a?.item?.set_number].join(":")}
    />
  );
}

function TrainSession() {
  const { data, act, run, busy } = useSession();

  const active = data?.view?.active;
  const item = active?.item;

  const [reps, setReps] = useState(item?.reps || 10);
  const [effort, setEffort] = useState(5);
  const [pain, setPain] = useState(0);
  const [symptoms, setSymptoms] = useState("");
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState("");
  const [source, setSource] = useState(false);
  const [minutes, setMinutes] = useState(3);

  const { width } = useWindowDimensions();

  // No active workout selected
  if (!active) {
    return (
      <Screen>
        <Title>Ready when you are</Title>

        <Card>
          <H>Choose a dated activity</H>

          <T>
            Your week brings strength, yoga, brain games and
            relaxation together.
          </T>

          <Button
            title="Choose an activity"
            onPress={() => router.push("/week")}
          />
        </Card>
      </Screen>
    );
  }

  const section = active.section;

  return (
    <Screen>
      <Title>{labels[section]}</Title>

      <Meta light>
        {active.date} · {active.minutes} min estimated
      </Meta>

      {active.finished ? (
        <Card>
          <Feather
            name="check-circle"
            size={32}
            color="#126bc5"
          />

          <H>
            {active.status === "completed"
              ? `Nice work, ${data?.state.profile.name}.`
              : "Activity ended"}
          </H>

          <T>
            {active.count}{" "}
            {section === "strength"
              ? "sets recorded"
              : section === "yoga"
                ? "poses recorded"
                : section === "brain"
                  ? "answers recorded"
                  : "minutes self-reported"}
          </T>

          {active.pain_warning && (
            <T accessibilityRole="alert">
              Pain reached 4 or more. The movement was eased or
              ended. Follow clinician guidance; an easier
              next-week goal still needs your acceptance.
            </T>
          )}

          <Meta>
            {data?.view?.next_activity
              ? `Next: ${
                  labels[data.view.next_activity.section]
                } · ${data.view.next_activity.date}`
              : "Review your recorded week on Progress."}
          </Meta>

          <Row>
            <Button
              title="Back to week"
              onPress={() => router.push("/week")}
            />

            <Button
              title="Review progress"
              variant="secondary"
              onPress={() => router.push("/progress")}
            />
          </Row>
        </Card>
      ) : (
        <>
          <Card>
            {item &&
              (section === "strength" ||
                section === "yoga") && (
                <>
                  <View
                    style={{
                      flexDirection:
                        width >= 900 ? "row" : "column",
                      gap: 24,
                    }}
                  >
                    {/* Exercise video / illustration */}
                    <View
                      style={{
                        width:
                          width >= 900 ? "40%" : "100%",
                        minHeight: 260,
                        borderRadius: 20,
                        backgroundColor: "#e8f3ff",
                        alignItems: "center",
                        justifyContent: "center",
                        overflow: "hidden",
                      }}
                    >
                      <ExerciseVideo
                        image={item.image}
                        name={item.name}
                        apiUrl={API_URL}
                      />
                    </View>

                    {/* Exercise instructions */}
                    <View
                      style={{
                        flex: 1,
                        gap: 12,
                      }}
                    >
                      <EvidenceBadge level={item.badge} />

                      <H>{item.name}</H>

                      <T>{item.version}</T>

                      {section === "strength" && (
                        <>
                          <H>
                            {item.sets} × {item.reps}{" "}
                            {item.unit}
                          </H>

                          <Meta>
                            Exercise {item.exercise_number} of{" "}
                            {item.exercise_total} · Set{" "}
                            {item.set_number} of {item.sets}
                          </Meta>

                          {item.power && (
                            <Chip
                              label="Power: lift with comfortable intent"
                            />
                          )}

                          <Chip
                            label={`Easier example: ${item.easier}`}
                          />

                          <Chip
                            label={`Harder example: ${item.harder}`}
                          />
                        </>
                      )}

                      <T>{item.cue}</T>

                      <Button
                        title="Why this exercise?"
                        variant="secondary"
                        onPress={() => setSource(true)}
                      />
                    </View>
                  </View>

                  {/* Repetition tracking */}
                  {section === "strength" && (
                    <Stepper
                      label={
                        item.unit === "seconds"
                          ? "Seconds"
                          : "Repetitions"
                      }
                      min={0}
                      max={100}
                      value={reps}
                      onChange={setReps}
                    />
                  )}

                  {/* Effort tracking */}
                  <Stepper
                    label="Effort"
                    value={effort}
                    onChange={setEffort}
                    min={1}
                    max={10}
                  />

                  {/* Pain tracking */}
                  <Stepper
                    label="Pain"
                    value={pain}
                    onChange={setPain}
                    min={0}
                    max={10}
                  />

                  <Button
                    title={
                      section === "strength"
                        ? "Record set"
                        : "Record pose"
                    }
                    busy={busy}
                    onPress={() =>
                      void run(async () => {
                        await act(
                          `/activities/active/${
                            section === "strength"
                              ? "set"
                              : "pose"
                          }`,
                          {
                            ...(section === "strength"
                              ? { reps }
                              : {}),
                            effort,
                            pain,
                          },
                        );
                      })
                    }
                  />
                </>
              )}

            {/* Brain games */}
            {section === "brain" && (
              <>
                <EvidenceBadge level="Emerging" />

                <H>{item?.question}</H>

                <Meta>
                  Enter the next number. Brain games are a
                  reasoning activity.
                </Meta>

                <Input
                  label="Your answer"
                  value={answer}
                  onChangeText={setAnswer}
                  keyboardType="number-pad"
                />

                <Row>
                  {[
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "0",
                    "−",
                    "Clear",
                  ].map((d) => (
                    <Button
                      key={d}
                      title={
                        d === "−"
                          ? "Negative sign"
                          : d
                      }
                      variant="secondary"
                      onPress={() =>
                        setAnswer(
                          d === "Clear"
                            ? ""
                            : answer +
                                (d === "−" ? "-" : d),
                        )
                      }
                    />
                  ))}
                </Row>

                <Button
                  title="Check answer"
                  disabled={!/^-?\d+$/.test(answer)}
                  onPress={() =>
                    void run(async () => {
                      const r = await act<{
                        explanation: string;
                        correct: boolean;
                      }>(
                        "/activities/active/answer",
                        {
                          answer: Number(answer),
                        },
                      );

                      setFeedback(
                        (r.correct
                          ? "Correct. "
                          : "Keep practising. ") +
                          r.explanation,
                      );

                      setAnswer("");
                    })
                  }
                />

                {feedback && (
                  <T accessibilityLiveRegion="polite">
                    {feedback}
                  </T>
                )}
              </>
            )}

            {/* Relaxation */}
            {section === "relaxation" && (
              <>
                <EvidenceBadge level="Moderate" />

                <H>A moment to settle</H>

                <Breathing />

                <Row>
                  {[3, 5].map((m) => (
                    <Button
                      key={m}
                      title={`${m} minutes`}
                      variant={
                        minutes === m
                          ? "primary"
                          : "secondary"
                      }
                      onPress={() => setMinutes(m)}
                    />
                  ))}
                </Row>

                <Button
                  title="Done — record my minutes"
                  onPress={() =>
                    void run(async () => {
                      await act(
                        "/activities/active/finish",
                        { minutes },
                      );
                    })
                  }
                />

                <Meta>
                  Your completion is self-reported.
                  No timer completes the activity for you.
                </Meta>
              </>
            )}
          </Card>

          {/* Rest timer */}
          {section === "strength" && (
            <Card>
              <RestTimer />
            </Card>
          )}

          <Button
            title="End activity early"
            variant="secondary"
            onPress={() =>
              void run(async () => {
                await act(
                  "/activities/active/finish",
                  { skipped: true },
                );
              })
            }
          />
        </>
      )}

      {/* Symptom reporting */}
      <Card>
        <H>
          {active.finished
            ? "Feeling unwell?"
            : "How are you feeling?"}
        </H>

        <T>
          If you have chest pain, dizziness or faintness,
          use Stop immediately.
        </T>

        <Input
          label="Symptoms or concerns"
          value={symptoms}
          onChangeText={setSymptoms}
          multiline
        />

        <Button
          title="Check symptoms"
          variant="danger"
          onPress={() =>
            void run(async () => {
              const r = await act<{
                message: string;
              }>("/symptoms", {
                text: symptoms,
              });

              setFeedback(r.message);
            })
          }
        />

        {feedback && (
          <T accessibilityLiveRegion="polite">
            {feedback}
          </T>
        )}
      </Card>

      {/* Evidence information */}
      <Sheet
        title="Why this exercise?"
        visible={source}
        onClose={() => setSource(false)}
      >
        <T>{item?.source}</T>

        <T>
          Use the displayed version and prescription.
          Evidence describes general activity,
          not a personal medical recommendation.
        </T>
      </Sheet>
    </Screen>
  );
}
