import { Redirect, router } from "expo-router";
import { Screen, Title, Card, H, T, Button, Meta } from "../components";
import { useSession } from "../session";
export default function Welcome() {
  const { token, data } = useSession();
  if (token && data)
    return (
      <Redirect
        href={
          data.state.plan
            ? "/today"
            : data.consented
              ? "/onboarding"
              : "/consent"
        }
      />
    );
  return (
    <Screen>
      <Title>Strength for the years ahead</Title>
      <Meta light>A complete week, at your pace.</Meta>
      <Card>
        <H>A little structure. Room for life.</H>
        <T>Build everyday strength and balance.</T>
        <T>Make space to stretch and unwind.</T>
        <T>Enjoy a reasoning challenge.</T>
        <Button
          title="Create account"
          onPress={() => router.push("/register")}
        />
        <Button
          title="Sign in"
          variant="secondary"
          onPress={() => router.push("/sign-in")}
        />
      </Card>
      <Button
        title="Consumer Health Data Privacy Policy"
        variant="secondary"
        onPress={() => router.push("/settings/privacy")}
      />
      <Meta light>Beta — content pending professional review.</Meta>
    </Screen>
  );
}
