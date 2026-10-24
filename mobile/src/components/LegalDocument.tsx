import { router } from "expo-router";
import legal from "../../content/legal.json";
import { Screen, Title, Card, H, T, Button } from "./index";
export default function LegalDocument({ kind }: { kind: "privacy" | "terms" }) {
  const text = String(
    legal[kind] || "Draft — pending legal review. Content unavailable.",
  );
  return (
    <Screen>
      <Title>{kind === "privacy" ? "Privacy policy" : "Terms"}</Title>
      <Card>
        {text
          .split("\n\n")
          .filter((block) => !block.startsWith("# "))
          .map((block, i) =>
            block.startsWith("## ") ? (
              <H key={i}>{block.slice(3)}</H>
            ) : (
              <T key={i} style={{ maxWidth: 720 }}>
                {block}
              </T>
            ),
          )}
        <Button
          title="Go back"
          variant="secondary"
          onPress={() => router.back()}
        />
      </Card>
    </Screen>
  );
}
