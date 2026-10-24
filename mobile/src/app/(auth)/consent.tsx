import { useState } from "react";
import { router } from "expo-router";
import { Screen, Title, Card, T, Check, Button, Meta } from "../../components";
import { useSession } from "../../session";
export default function Consent() {
  const [agree, setAgree] = useState(false);
  const { run, act, busy } = useSession();
  return (
    <Screen>
      <Title>Your information, your choice</Title>
      <Card>
        <T>
          ZINC saves your profile, safety answers, activity logs and coach
          conversations to prepare your week and keep a record you can return
          to.
        </T>
        <T>
          No advertising or third-party analytics. No sale or sharing for
          advertising. If you use the AI coach, the relevant plan and feedback
          are sent to Gemini to answer your request.
        </T>
        <T>
          You can download your information or delete your account in Settings.
          Please avoid adding information you do not want stored.
        </T>
        <Meta>
          Beta — content pending professional review. This build has had no
          clinical or legal review.
        </Meta>
        <Button
          title="Read privacy information"
          variant="secondary"
          onPress={() => router.push("/settings/privacy")}
        />
        <Check
          label="I agree to ZINC collecting and storing my health-related information for these features"
          value={agree}
          onChange={setAgree}
        />
        <Button
          title="Agree and continue"
          disabled={!agree}
          busy={busy}
          onPress={() =>
            void run(async () => {
              await act("/consent", {
                collect_health_data: true,
                version: "2026-10-beta",
              });
              router.replace("/onboarding");
            })
          }
        />
      </Card>
    </Screen>
  );
}
