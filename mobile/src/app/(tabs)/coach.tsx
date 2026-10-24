import { useEffect, useState } from "react";
import {
  Screen,
  Title,
  Card,
  H,
  T,
  Meta,
  Input,
  Button,
  Row,
  Sheet,
} from "../../components";
import { useSession } from "../../session";
import { useReducedMotion } from "../../theme";
export default function Coach() {
  const { data, act, run, busy } = useSession();
  const [message, setMessage] = useState(""),
    [rules, setRules] = useState(false),
    [exercise, setExercise] = useState("sit_to_stand"),
    [direction, setDirection] = useState("same");
  const messages = data?.state.messages || [],
    last = messages.at(-1),
    proposal = data?.state.pending_change;

  async function send(text: string) {
    if (!text.trim()) return;
    await run(async () => {
      await act("/coach", { message: text });
      setMessage("");
    });
  }
  return (
    <Screen>
      <Title>Your coach</Title>
      <Meta light>Your plan. Your pace. You decide what changes.</Meta>
      {!messages.length && (
        <Card>
          <T>
            Hi {data?.state.profile.name} — I can explain your plan, review how
            your week went, and suggest next week’s goal. You decide what
            changes.
          </T>
        </Card>
      )}
      {messages.map((m, i) => (
        <Card key={i}>
          <Meta>{m.role === "user" ? "You" : "Coach"}</Meta>
          {m === last && m.role === "assistant" ? (
            <CoachReply key={messages.length} text={m.text} />
          ) : (
            <T>{m.text}</T>
          )}
        </Card>
      ))}
      {busy && (
        <T accessibilityLiveRegion="polite" style={{ color: "white" }}>
          Reviewing your week…
        </T>
      )}
      <Row>
        {[
          "Why this exercise?",
          "My knee feels sore",
          "What’s next week?",
          "Weekly check-in",
        ].map((v) => (
          <Button
            key={v}
            title={v}
            variant="secondary"
            onPress={() => void send(v)}
          />
        ))}
      </Row>
      <Card>
        <Input
          label="Ask your coach"
          value={message}
          onChangeText={setMessage}
          multiline
          maxLength={2000}
        />
        <Button
          title="Send message"
          busy={busy}
          disabled={!message.trim()}
          onPress={() => void send(message)}
        />
      </Card>
      {proposal && (
        <Card>
          <H>For next week — your choice</H>
          <T>
            {
              data?.state.plan?.exercises.find(
                (e) => e.id === proposal.exercise_id,
              )?.name
            }
          </T>
          <H>
            {proposal.current} → {proposal.proposed}
          </H>
          <T>{proposal.reason}</T>
          <Row>
            <Button
              title="Accept for next week"
              disabled={!data?.view?.can_accept}
              onPress={() =>
                void run(async () => {
                  await act("/proposal/accept");
                })
              }
            />
            <Button
              title="Decline — keep my plan"
              variant="secondary"
              onPress={() =>
                void run(async () => {
                  await act("/proposal/decline");
                })
              }
            />
          </Row>
          {!data?.view?.can_accept && (
            <Meta>Finish or end unfinished activities before accepting.</Meta>
          )}
        </Card>
      )}
      <Button
        title="Adjust without AI"
        variant="secondary"
        onPress={() => setRules(true)}
      />
      <Sheet
        title="Adjust without AI"
        visible={rules}
        onClose={() => setRules(false)}
      >
        <Meta>
          Log strength feedback first. Finish the current activity before
          accepting. Preview never changes your prescription.
        </Meta>
        <Row>
          {data?.state.plan?.exercises.map((e) => (
            <Button
              key={e.id}
              title={e.name}
              variant={exercise === e.id ? "primary" : "secondary"}
              onPress={() => setExercise(e.id)}
            />
          ))}
        </Row>
        <Row>
          {["same", "harder", "easier"].map((d) => (
            <Button
              key={d}
              title={d}
              variant={direction === d ? "primary" : "secondary"}
              onPress={() => setDirection(d)}
            />
          ))}
        </Row>
        <Button
          title="Preview adjustment"
          onPress={() =>
            void run(async () => {
              await act("/proposal/preview", {
                exercise_id: exercise,
                direction,
              });
              setRules(false);
            })
          }
        />
      </Sheet>
    </Screen>
  );
}

function CoachReply({ text }: { text: string }) {
  const reduce = useReducedMotion();
  const [length, setLength] = useState(0);
  useEffect(() => {
    if (reduce) return;
    const timer = setInterval(
      () => setLength((n) => Math.min(text.length, n + 5)),
      20,
    );
    return () => clearInterval(timer);
  }, [text, reduce]);
  return <T>{reduce ? text : text.slice(0, length)}</T>;
}
