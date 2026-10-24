import { StatusBar } from "expo-status-bar";
import { Stack, router, usePathname } from "expo-router";
import { useFonts, Manrope_700Bold } from "@expo-google-fonts/manrope";
import {
  DMSans_400Regular,
  DMSans_600SemiBold,
} from "@expo-google-fonts/dm-sans";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";
import { View } from "react-native";
import { useEffect } from "react";
import { syncReminders } from "../reminders";
import { PreferencesProvider } from "../theme";
import { SessionProvider, useSession } from "../session";
import { Screen, Title, T, Row, Button, StopButton } from "../components";
function Shell() {
  const { token, data, ready, busy, error, stop } = useSession();
  const path = usePathname();
  useEffect(() => {
    if (
      ready &&
      !token &&
      ![
        "/",
        "/sign-in",
        "/register",
        "/settings/privacy",
        "/settings/terms",
      ].includes(path)
    )
      router.replace("/");
  }, [ready, token, path]);
  useEffect(() => {
    if (ready)
      void syncReminders(
        data?.user?.email,
        data?.state.plan?.days,
        data?.state.stopped,
      ).catch(() => {});
  }, [ready, data?.user?.email, data?.state.plan?.days, data?.state.stopped]);
  const planned = !!data?.state.plan,
    stopped = data?.state.stopped;
  useEffect(() => {
    if (stopped && !path.startsWith("/settings") && path !== "/stopped")
      router.replace("/stopped");
  }, [stopped, path]);
  return (
    <SafeAreaView
      style={{ flex: 1, backgroundColor: "#063774" }}
      edges={["top", "left", "right"]}
    >
      <View
        style={{
          width: "100%",
          maxWidth: 1080,
          alignSelf: "center",
          paddingHorizontal: 20,
          paddingVertical: 12,
          gap: 10,
        }}
      >
        <Row>
          <T
            style={{
              color: "white",
              fontFamily: "Manrope_700Bold",
              fontSize: 26,
              flex: 1,
            }}
          >
            ZINC <T style={{ color: "#d5e9ff", fontSize: 13 }}>Beta</T>
          </T>
          {token && (
            <Button
              title="Settings"
              variant="secondary"
              onPress={() => router.push("/settings")}
            />
          )}
          {planned &&
            (!data?.view?.active || data.view.active.finished || stopped) && (
              <StopButton onPress={() => void stop()} />
            )}
        </Row>
        {planned &&
          !stopped &&
          data?.view?.active &&
          !data.view.active.finished && (
            <StopButton full onPress={() => void stop()} />
          )}
        {error ? (
          <T accessibilityRole="alert" style={{ color: "white" }}>
            {error}
          </T>
        ) : null}
      </View>
      <View style={{ flex: 1 }} pointerEvents={busy ? "none" : "auto"}>
        {busy && (
          <T
            accessibilityLiveRegion="polite"
            style={{
              backgroundColor: "#e8f3ff",
              padding: 8,
              textAlign: "center",
            }}
          >
            Saving or reviewing…
          </T>
        )}
        <Stack screenOptions={{ headerShown: false }} />
      </View>
    </SafeAreaView>
  );
}
export default function RootLayout() {
  const [loaded, error] = useFonts({
    Manrope_700Bold,
    DMSans_400Regular,
    DMSans_600SemiBold,
  });
  return (
    <SafeAreaProvider>
      <StatusBar style="light" />
      <PreferencesProvider>
        {!loaded && !error ? (
          <Screen>
            <Title>Loading ZINC…</Title>
          </Screen>
        ) : (
          <SessionProvider>
            <Shell />
          </SessionProvider>
        )}
      </PreferencesProvider>
    </SafeAreaProvider>
  );
}
