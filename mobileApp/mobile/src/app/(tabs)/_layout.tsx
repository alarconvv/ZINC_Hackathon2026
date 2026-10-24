import { Tabs, Redirect } from "expo-router";
import { Feather } from "@expo/vector-icons";
import { useSession } from "../../session";
import { colors, fonts } from "../../theme";
import { Screen, Title } from "../../components";
export default function TabLayout() {
  const { data, ready } = useSession();
  if (!ready)
    return (
      <Screen>
        <Title>Loading your week…</Title>
      </Screen>
    );
  if (!data?.state.plan) return <Redirect href="/" />;
  if (data.state.stopped) return <Redirect href="/stopped" />;
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.blue,
        tabBarInactiveTintColor: colors.ink,
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.rule,
          minHeight: 78,
          paddingTop: 10,
          paddingBottom: 16,
        },
        tabBarLabelStyle: { fontFamily: fonts.medium, fontSize: 12 },
        sceneStyle: { backgroundColor: colors.ocean },
      }}
    >
      {(["today", "week", "train", "coach", "progress"] as const).map(
        (name, i) => (
          <Tabs.Screen
            key={name}
            name={name}
            options={{
              title: ["Today", "Week", "Train", "Coach", "Progress"][i],
              tabBarAccessibilityLabel: [
                "Today",
                "Week",
                "Train",
                "Coach",
                "Progress",
              ][i],
              tabBarIcon: ({ color, size }) => (
                <Feather
                  name={
                    (
                      [
                        "home",
                        "calendar",
                        "activity",
                        "message-circle",
                        "trending-up",
                      ] as const
                    )[i]
                  }
                  color={typeof color === "string" ? color : colors.ink}
                  size={size}
                />
              ),
            }}
          />
        ),
      )}
    </Tabs>
  );
}
