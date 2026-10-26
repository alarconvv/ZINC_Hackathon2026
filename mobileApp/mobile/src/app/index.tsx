
import React, { useState } from "react";
import {
  View,
  Text,
  Pressable,
  StyleSheet,
  useWindowDimensions,
} from "react-native";
import { Feather } from "@expo/vector-icons";
import { Redirect, router } from "expo-router";

import { Screen } from "../components";
import { useSession } from "../session";
import HoverCard from "../components/HoverCard";

// ---------------------------------------------
// ZINC BRAND COLORS
// ---------------------------------------------

const COLORS = {
  navy: "#063774",
  dark: "#052B5D",
  blue: "#126BC5",
  bright: "#1682F2",
  sky: "#8DD8FF",
  white: "#FFFFFF",
  pale: "#E8F3FF",
  ink: "#12355B",
  muted: "#58728D",
  green: "#1B9C83",
  border: "#DCE8F4",
};

type IconName = React.ComponentProps<typeof Feather>["name"];

// ---------------------------------------------
// PRIMARY BUTTONS
// ---------------------------------------------

function HeroButton({
  title,
  icon,
  secondary = false,
  onPress,
  wide = false,
}: {
  title: string;
  icon?: IconName;
  secondary?: boolean;
  onPress: () => void;
  wide?: boolean;
}) {
  const [hovered, setHovered] = useState(false);

  return (
    <HoverCard
      interactive
      onPress={onPress}
      accessibilityLabel={title}
      style={{ width: wide ? "100%" : undefined }}
    >
      <View
        style={[
          styles.heroButton,
          secondary
            ? styles.secondaryButton
            : styles.primaryButton,
          hovered && styles.buttonHovered,
        ]}
        onPointerEnter={() => setHovered(true)}
        onPointerLeave={() => setHovered(false)}
      >
        <Text style={styles.heroButtonText}>
          {title}
        </Text>

        {icon && (
          <Feather
            name={icon}
            size={19}
            color={COLORS.navy}
          />
        )}
      </View>
    </HoverCard>
  );
}

// ---------------------------------------------
// DASHBOARD METRIC
// ---------------------------------------------

function MetricCard({
  icon,
  value,
  label,
}: {
  icon: IconName;
  value: string;
  label: string;
}) {
  return (
    <View style={styles.metricCard}>
      <Feather
        name={icon}
        size={22}
        color={COLORS.bright}
      />

      <Text style={styles.metricValue}>
        {value}
      </Text>

      <Text style={styles.metricLabel}>
        {label}
      </Text>
    </View>
  );
}

// ---------------------------------------------
// ACTIVITY PROGRESS
// ---------------------------------------------

function ProgressRow({
  name,
  icon,
  completed,
  total,
}: {
  name: string;
  icon: IconName;
  completed: number;
  total: number;
}) {
  const progress = total > 0
    ? Math.min(100, (completed / total) * 100)
    : 0;

  return (
    <View style={styles.progressBlock}>
      <View style={styles.progressHeader}>
        <View style={styles.progressName}>
          <Feather
            name={icon}
            size={18}
            color={COLORS.bright}
          />

          <Text style={styles.progressTitle}>
            {name}
          </Text>
        </View>

        <Text style={styles.progressValue}>
          {completed}/{total}
        </Text>
      </View>

      <View style={styles.progressTrack}>
        <View
          style={[
            styles.progressFill,
            { width: `${progress}%` },
          ]}
        />
      </View>
    </View>
  );
}

// ---------------------------------------------
// FLOATING DASHBOARD PREVIEW
// ---------------------------------------------

function DashboardPreview() {
  return (
    <View style={styles.dashboard}>
      <View style={styles.dashboardHeader}>
        <View style={{ flex: 1, gap: 5 }}>
          <Text style={styles.dashboardEyebrow}>
            YOUR WELLNESS SPACE
          </Text>

          <Text style={styles.dashboardTitle}>
            Your week, simplified.
          </Text>
        </View>

        <View style={styles.dashboardIcon}>
          <Feather
            name="activity"
            size={26}
            color={COLORS.bright}
          />
        </View>
      </View>

      {/* Key metrics */}
      <View style={styles.metricsRow}>
        <MetricCard
          icon="calendar"
          value="7 days"
          label="Flexible plans"
        />

        <MetricCard
          icon="heart"
          value="4 areas"
          label="Whole-person wellness"
        />

        <MetricCard
          icon="message-circle"
          value="AI"
          label="Coach support"
        />
      </View>

      <View style={styles.divider} />

      <View style={{ gap: 5 }}>
        <Text style={styles.dashboardSectionTitle}>
          A balanced routine
        </Text>

        <Text style={styles.dashboardCaption}>
          An illustrative weekly plan preview
        </Text>
      </View>

      <View style={styles.progressList}>
        <ProgressRow
          name="Strength & balance"
          icon="activity"
          completed={2}
          total={3}
        />

        <ProgressRow
          name="Yoga & movement"
          icon="sun"
          completed={1}
          total={2}
        />

        <ProgressRow
          name="Brain games"
          icon="cpu"
          completed={1}
          total={2}
        />

        <ProgressRow
          name="Relaxation"
          icon="moon"
          completed={2}
          total={2}
        />
      </View>

      {/* Coach preview */}
      <View style={styles.coachPanel}>
        <View style={styles.coachIcon}>
          <Feather
            name="message-circle"
            size={21}
            color={COLORS.white}
          />
        </View>

        <View style={{ flex: 1, gap: 5 }}>
          <Text style={styles.coachTitle}>
            Your AI wellness coach
          </Text>

          <Text style={styles.coachDescription}>
            Get guidance, understand your plan, and
            stay in control of suggested changes.
          </Text>
        </View>
      </View>

      <Text style={styles.previewNote}>
        Illustrative preview · Not personal activity data
      </Text>
    </View>
  );
}

// ---------------------------------------------
// FEATURES WITH HOVER ANIMATION
// ---------------------------------------------

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: IconName;
  title: string;
  description: string;
}) {
  return (
    <HoverCard style={{ flex: 1, minWidth: 0 }}>
      <View style={styles.featureCard}>
        <View style={styles.featureIcon}>
          <Feather
            name={icon}
            size={25}
            color={COLORS.bright}
          />
        </View>

        <View style={{ flex: 1, gap: 7 }}>
          <Text style={styles.featureTitle}>
            {title}
          </Text>

          <Text style={styles.featureDescription}>
            {description}
          </Text>
        </View>
      </View>
    </HoverCard>
  );
}

// ---------------------------------------------
// LANDING PAGE
// ---------------------------------------------

export default function Welcome() {
  const { token, data } = useSession();
  const { width } = useWindowDimensions();

  // Keep existing ZINC authentication redirects.
  if (token && data) {
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
  }

  const desktop = width >= 900;
  const compact = width < 600;

  return (
    <Screen>
      <View style={styles.page}>
        {/* ----------------------------------
            HERO SECTION
        ---------------------------------- */}

        <View
          style={[
            styles.heroSection,
            {
              flexDirection:
                desktop ? "row" : "column",
            },
          ]}
        >
          {/* LEFT SIDE */}
          <View
            style={[
              styles.heroLeft,
              { flex: desktop ? 1 : undefined },
            ]}
          >
            <View style={styles.eyebrow}>
              <Feather
                name="heart"
                size={15}
                color="#BDE7FF"
              />

              <Text style={styles.eyebrowText}>
                YOUR WELLNESS. YOUR WAY.
              </Text>
            </View>

            <Text
              style={[
                styles.heroTitle,
                compact && styles.heroTitleMobile,
              ]}
            >
              Feel stronger.
              {"\n"}
              Live better.
              {"\n"}
              <Text style={styles.heroHighlight}>
                Every week.
              </Text>
            </Text>

            <Text style={styles.heroDescription}>
              Meet ZINC, your AI-assisted wellness
              companion. Build strength, move with
              confidence, and create a weekly routine
              that fits your life.
            </Text>

            {/* CTA buttons */}
            <View
              style={[
                styles.heroActions,
                {
                  flexDirection:
                    compact ? "column" : "row",
                },
              ]}
            >
              <HeroButton
                title="Get started"
                icon="arrow-right"
                wide={compact}
                onPress={() =>
                  router.push("/register")
                }
              />

              <HeroButton
                title="Sign in"
                secondary
                wide={compact}
                onPress={() =>
                  router.push("/sign-in")
                }
              />
            </View>

            {/* Trust message */}
            <View style={styles.trustRow}>
              <Feather
                name="shield"
                size={18}
                color="#BDE7FF"
              />

              <Text style={styles.trustText}>
                Your pace. Your choices. Your progress.
              </Text>
            </View>
          </View>

          {/* RIGHT SIDE: FLOATING DASHBOARD */}
          <View
            style={[
              styles.dashboardColumn,
              { flex: desktop ? 1 : undefined },
            ]}
          >
            <HoverCard floating>
              <DashboardPreview />
            </HoverCard>
          </View>
        </View>

        {/* ----------------------------------
            FEATURES
        ---------------------------------- */}

        <View style={styles.featuresSection}>
          <Text style={styles.sectionEyebrow}>
            BUILT AROUND REAL LIFE
          </Text>

          <Text
            style={[
              styles.sectionTitle,
              compact && { fontSize: 25 },
            ]}
          >
            More than a workout plan.
          </Text>

          <View
            style={[
              styles.featuresGrid,
              {
                flexDirection:
                  desktop ? "row" : "column",
              },
            ]}
          >
            <FeatureCard
              icon="calendar"
              title="A plan that fits"
              description="Organize strength, yoga, brain games, and relaxation into a manageable week."
            />

            <FeatureCard
              icon="play-circle"
              title="Learn as you move"
              description="Follow clear exercise instructions and available video demonstrations."
            />

            <FeatureCard
              icon="message-circle"
              title="Coaching with control"
              description="Ask Gemini-powered coaching questions and approve proposed goal changes yourself."
            />
          </View>
        </View>

        {/* ----------------------------------
            FOOTER
        ---------------------------------- */}

        <View style={styles.footer}>
          <Pressable
            accessibilityRole="link"
            onPress={() =>
              router.push("/settings/privacy")
            }
          >
            <Text style={styles.footerLink}>
              Consumer Health Data Privacy Policy
            </Text>
          </Pressable>

          <Text style={styles.footerText}>
            ZINC Beta · Content pending professional review.
          </Text>

          <Text style={styles.footerText}>
            General wellness, not medical advice.
          </Text>
        </View>
      </View>
    </Screen>
  );
}

// ---------------------------------------------
// STYLES
// ---------------------------------------------

const styles = StyleSheet.create({
  page: {
    width: "100%",
    paddingTop: 28,
    paddingBottom: 36,
    gap: 65,
  },

  heroSection: {
    width: "100%",
    gap: 42,
    alignItems: "center",
  },

  heroLeft: {
    width: "100%",
    minWidth: 0,
    gap: 26,
    justifyContent: "center",
  },

  eyebrow: {
    alignSelf: "flex-start",
    flexDirection: "row",
    alignItems: "center",
    gap: 9,
    paddingHorizontal: 15,
    paddingVertical: 10,
    backgroundColor: "rgba(255,255,255,0.10)",
    borderRadius: 100,
  },

  eyebrowText: {
    color: "#D9F2FF",
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 1.2,
  },

  heroTitle: {
    fontFamily: "Manrope_700Bold",
    color: COLORS.white,
    fontSize: 47,
    lineHeight: 61,
    letterSpacing: -1.3,
  },

  heroTitleMobile: {
    fontSize: 37,
    lineHeight: 49,
  },

  heroHighlight: {
    color: COLORS.sky,
  },

  heroDescription: {
    fontFamily: "DMSans_400Regular",
    color: "#E0EEFF",
    fontSize: 17,
    lineHeight: 29,
    maxWidth: 480,
  },

  heroActions: {
    gap: 13,
    flexWrap: "wrap",
    alignItems: "stretch",
  },

  heroButton: {
    minHeight: 56,
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 16,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 16,
  },

  primaryButton: {
    backgroundColor: "#FFFFFF",
  },

  secondaryButton: {
    backgroundColor: "#DCEEFF",
  },

  buttonHovered: {
    shadowColor: "#8DD8FF",
    shadowOpacity: 0.35,
    shadowRadius: 16,
    elevation: 5,
  },

  heroButtonText: {
    color: COLORS.navy,
    fontFamily: "DMSans_600SemiBold",
    fontSize: 16,
  },

  trustRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },

  trustText: {
    color: "#CDE7FC",
    fontSize: 13,
    flexShrink: 1,
  },

  dashboardColumn: {
    width: "100%",
    minWidth: 0,
    paddingVertical: 12,
  },

  dashboard: {
    width: "100%",
    backgroundColor: "#F9FCFF",
    borderRadius: 28,
    padding: 25,
    gap: 23,
    shadowColor: "#001C46",
    shadowOffset: {
      width: 0,
      height: 18,
    },
    shadowOpacity: 0.24,
    shadowRadius: 34,
    elevation: 8,
  },

  dashboardHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    justifyContent: "space-between",
  },

  dashboardEyebrow: {
    color: COLORS.bright,
    fontSize: 10,
    fontWeight: "700",
    letterSpacing: 1.5,
  },

  dashboardTitle: {
    color: COLORS.ink,
    fontFamily: "Manrope_700Bold",
    fontSize: 23,
  },

  dashboardIcon: {
    width: 51,
    height: 51,
    borderRadius: 16,
    backgroundColor: "#DFEFFF",
    alignItems: "center",
    justifyContent: "center",
  },

  metricsRow: {
    flexDirection: "row",
    gap: 9,
  },

  metricCard: {
    flex: 1,
    minWidth: 0,
    backgroundColor: "#E7F3FF",
    borderRadius: 15,
    alignItems: "center",
    paddingVertical: 14,
    paddingHorizontal: 5,
    gap: 7,
  },

  metricValue: {
    color: COLORS.ink,
    fontFamily: "Manrope_700Bold",
    fontSize: 16,
    textAlign: "center",
  },

  metricLabel: {
    color: COLORS.muted,
    fontSize: 10,
    lineHeight: 14,
    textAlign: "center",
  },

  divider: {
    width: "100%",
    height: 1,
    backgroundColor: COLORS.border,
  },

  dashboardSectionTitle: {
    color: COLORS.ink,
    fontFamily: "Manrope_700Bold",
    fontSize: 18,
  },

  dashboardCaption: {
    color: COLORS.muted,
    fontSize: 12,
  },

  progressList: {
    gap: 19,
  },

  progressBlock: {
    gap: 9,
  },

  progressHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 10,
  },

  progressName: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    flexShrink: 1,
  },

  progressTitle: {
    color: COLORS.ink,
    fontSize: 13,
    fontWeight: "600",
    flexShrink: 1,
  },

  progressValue: {
    color: COLORS.ink,
    fontSize: 12,
    fontWeight: "700",
  },

  progressTrack: {
    height: 9,
    backgroundColor: "#DCE9F5",
    borderRadius: 10,
    overflow: "hidden",
  },

  progressFill: {
    height: "100%",
    backgroundColor: COLORS.bright,
    borderRadius: 10,
  },

  coachPanel: {
    flexDirection: "row",
    alignItems: "center",
    gap: 13,
    backgroundColor: "#E4F1FF",
    borderRadius: 17,
    padding: 17,
  },

  coachIcon: {
    width: 46,
    height: 46,
    backgroundColor: COLORS.bright,
    borderRadius: 13,
    alignItems: "center",
    justifyContent: "center",
  },

  coachTitle: {
    color: COLORS.ink,
    fontSize: 14,
    fontWeight: "700",
  },

  coachDescription: {
    color: COLORS.muted,
    fontSize: 12,
    lineHeight: 19,
  },

  previewNote: {
    color: COLORS.muted,
    fontSize: 10,
    textAlign: "center",
  },

  featuresSection: {
    width: "100%",
    gap: 18,
  },

  sectionEyebrow: {
    color: "#AFE1FF",
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 1.5,
  },

  sectionTitle: {
    color: COLORS.white,
    fontFamily: "Manrope_700Bold",
    fontSize: 31,
    lineHeight: 41,
  },

  featuresGrid: {
    width: "100%",
    gap: 16,
    alignItems: "stretch",
  },

  featureCard: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 14,
    backgroundColor: "#F8FBFF",
    borderRadius: 19,
    padding: 19,
    minHeight: 143,
    shadowColor: "#002554",
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.08,
    shadowRadius: 12,
  },

  featureIcon: {
    width: 47,
    height: 47,
    backgroundColor: "#DAEEFF",
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
  },

  featureTitle: {
    color: COLORS.ink,
    fontFamily: "Manrope_700Bold",
    fontSize: 15,
  },

  featureDescription: {
    color: COLORS.muted,
    fontSize: 13,
    lineHeight: 21,
  },

  footer: {
    width: "100%",
    borderTopWidth: 1,
    borderTopColor: "rgba(255,255,255,0.17)",
    paddingTop: 24,
    gap: 12,
  },

  footerLink: {
    color: "#E6F3FF",
    textDecorationLine: "underline",
    fontSize: 14,
  },

  footerText: {
    color: "#C7E0F7",
    fontSize: 12,
  },
});
