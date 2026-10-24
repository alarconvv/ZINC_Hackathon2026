import React from "react";
import {
  ActivityIndicator,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TextInputProps,
  TextProps,
  View,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import Svg, { Circle } from "react-native-svg";
import { Feather } from "@expo/vector-icons";
import { colors as c, fonts, usePreferences } from "../theme";
export function T({ style, ...props }: TextProps) {
  const { large } = usePreferences();
  return (
    <Text
      allowFontScaling
      {...props}
      style={[
        {
          fontFamily: fonts.body,
          fontSize: large ? 19 : 16,
          lineHeight: large ? 29 : 25,
          color: c.ink,
        },
        style,
      ]}
    />
  );
}
export function Title({ children }: React.PropsWithChildren) {
  return (
    <T
      accessibilityRole="header"
      style={{
        fontFamily: fonts.heading,
        fontSize: 30,
        lineHeight: 39,
        color: "white",
        marginTop: 8,
        marginBottom: 8,
      }}
    >
      {children}
    </T>
  );
}
export function H({ children }: React.PropsWithChildren) {
  return (
    <T
      accessibilityRole="header"
      style={{ fontFamily: fonts.heading, fontSize: 22, lineHeight: 30 }}
    >
      {children}
    </T>
  );
}
export function Meta({
  children,
  light = false,
}: React.PropsWithChildren<{ light?: boolean }>) {
  return (
    <T style={{ fontSize: 14, color: light ? "#d5e9ff" : c.muted }}>
      {children}
    </T>
  );
}
export function SectionHeader({ children }: React.PropsWithChildren) {
  return (
    <T
      accessibilityRole="header"
      style={{ fontFamily: fonts.medium, fontSize: 14, color: c.muted }}
    >
      {children}
    </T>
  );
}
export function Screen({ children }: React.PropsWithChildren) {
  const { contrast } = usePreferences();
  return (
    <LinearGradient
      colors={contrast ? [c.ocean, c.ocean] : [c.blue, c.ocean]}
      style={{ flex: 1 }}
    >
      <ScrollView
        keyboardShouldPersistTaps="handled"
        contentContainerStyle={{ padding: 20, paddingBottom: 48, flexGrow: 1 }}
      >
        <View
          style={{
            width: "100%",
            maxWidth: 1040,
            alignSelf: "center",
            gap: 18,
          }}
        >
          {children}
          <Meta light>General wellness, not medical advice.</Meta>
        </View>
      </ScrollView>
    </LinearGradient>
  );
}
export function Card({
  children,
  testID,
}: React.PropsWithChildren<{ testID?: string }>) {
  return (
    <View
      testID={testID}
      style={{
        backgroundColor: c.surface,
        borderRadius: 24,
        padding: 24,
        gap: 14,
      }}
    >
      {children}
    </View>
  );
}
export function Row({ children }: React.PropsWithChildren) {
  return (
    <View
      style={{
        flexDirection: "row",
        alignItems: "center",
        gap: 10,
        flexWrap: "wrap",
      }}
    >
      {children}
    </View>
  );
}
export function Button({
  title,
  onPress,
  variant = "primary",
  disabled = false,
  busy = false,
}: {
  title: string;
  onPress: () => void;
  variant?: "primary" | "secondary" | "danger";
  disabled?: boolean;
  busy?: boolean;
}) {
  const [focused, setFocused] = React.useState(false);
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={title}
      accessibilityState={{ disabled: disabled || busy, busy }}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      disabled={disabled || busy}
      onPress={onPress}
      style={({ pressed }) => ({
        minHeight: 48,
        borderRadius: 24,
        paddingHorizontal: 20,
        paddingVertical: 12,
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: disabled
          ? "#d6e7f5"
          : variant === "primary"
            ? c.blue
            : variant === "danger"
              ? "#fff7f7"
              : c.pale,
        borderWidth: 3,
        borderColor: focused
          ? c.ink
          : variant === "danger"
            ? c.danger
            : "transparent",
        opacity: pressed ? 0.78 : 1,
      })}
    >
      {busy ? (
        <ActivityIndicator color={variant === "primary" ? "white" : c.ink} />
      ) : (
        <T
          style={{
            fontFamily: fonts.medium,
            color: disabled
              ? c.muted
              : variant === "primary"
                ? "white"
                : variant === "danger"
                  ? c.danger
                  : c.ink,
            textAlign: "center",
          }}
        >
          {title}
        </T>
      )}
    </Pressable>
  );
}
export function StopButton({
  onPress,
  full = false,
  busy = false,
}: {
  onPress: () => void;
  full?: boolean;
  busy?: boolean;
}) {
  return (
    <Button
      title={full ? "Stop — chest pain, dizziness or faintness" : "Stop"}
      variant="danger"
      onPress={onPress}
      busy={busy}
    />
  );
}
export function Chip({ label }: { label: string }) {
  return (
    <View
      style={{
        backgroundColor: c.pale,
        borderRadius: 16,
        paddingHorizontal: 12,
        paddingVertical: 4,
      }}
    >
      <T style={{ fontSize: 13, fontFamily: fonts.medium }}>{label}</T>
    </View>
  );
}
export function EvidenceBadge({ level }: { level: string }) {
  return <Chip label={`${level} evidence`} />;
}
export function Ring({
  percent,
  label,
  size = 100,
}: {
  percent: number;
  label: string;
  size?: number;
}) {
  const radius = 40,
    length = 2 * Math.PI * radius;
  return (
    <View
      accessibilityLabel={label}
      accessibilityRole="image"
      style={{
        width: size,
        height: size,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <Svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        style={StyleSheet.absoluteFill}
      >
        <Circle
          cx="50"
          cy="50"
          r={radius}
          stroke={c.rule}
          strokeWidth="6"
          fill="none"
        />
        <Circle
          cx="50"
          cy="50"
          r={radius}
          stroke={c.blue}
          strokeWidth="6"
          fill="none"
          strokeDasharray={`${(length * percent) / 100} ${length}`}
          rotation="-90"
          origin="50,50"
          strokeLinecap="round"
        />
      </Svg>
      <T style={{ fontFamily: fonts.heading, fontSize: size > 90 ? 25 : 16 }}>
        {label}
      </T>
    </View>
  );
}
export function Input({ label, ...props }: TextInputProps & { label: string }) {
  return (
    <View style={{ gap: 6 }}>
      <T style={{ fontFamily: fonts.medium }}>{label}</T>
      <TextInput
        allowFontScaling
        accessibilityLabel={label}
        placeholderTextColor={c.muted}
        {...props}
        style={[
          {
            minHeight: 52,
            borderWidth: 1,
            borderColor: c.muted,
            borderRadius: 16,
            padding: 14,
            color: c.ink,
            fontSize: 16,
            fontFamily: fonts.body,
            backgroundColor: "white",
          },
          props.style,
        ]}
      />
    </View>
  );
}
export function Check({
  label,
  value,
  onChange,
}: {
  label: string;
  value: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <Pressable
      accessibilityRole="checkbox"
      accessibilityLabel={label}
      accessibilityState={{ checked: value }}
      onPress={() => onChange(!value)}
      style={{
        minHeight: 48,
        flexDirection: "row",
        gap: 12,
        alignItems: "center",
      }}
    >
      <Feather
        name={value ? "check-square" : "square"}
        size={24}
        color={c.blue}
      />
      <T style={{ flex: 1 }}>{label}</T>
    </Pressable>
  );
}
export function Stepper({
  label,
  value,
  onChange,
  min,
  max,
}: {
  label: string;
  value: number;
  onChange: (n: number) => void;
  min: number;
  max: number;
}) {
  return (
    <View style={{ gap: 6 }}>
      <T>
        {label}: {value}
      </T>
      <Row>
        <Button
          title={`Decrease ${label}`}
          variant="secondary"
          disabled={value <= min}
          onPress={() => onChange(value - 1)}
        />
        <Button
          title={`Increase ${label}`}
          variant="secondary"
          disabled={value >= max}
          onPress={() => onChange(value + 1)}
        />
      </Row>
    </View>
  );
}
export function Sheet({
  title,
  visible,
  onClose,
  children,
}: React.PropsWithChildren<{
  title: string;
  visible: boolean;
  onClose: () => void;
}>) {
  return (
    <Modal
      visible={visible}
      transparent
      animationType="none"
      onRequestClose={onClose}
    >
      <View
        accessibilityViewIsModal
        style={{
          flex: 1,
          backgroundColor: "#031f40aa",
          justifyContent: "center",
          padding: 20,
        }}
      >
        <ScrollView contentContainerStyle={{ paddingVertical: 20 }}>
          <View style={{ maxWidth: 600, width: "100%", alignSelf: "center" }}>
            <Card>
              <H>{title}</H>
              {children}
              <Button title="Close" variant="secondary" onPress={onClose} />
            </Card>
          </View>
        </ScrollView>
      </View>
    </Modal>
  );
}

export function IconButton({
  name,
  label,
  onPress,
}: {
  name: React.ComponentProps<typeof Feather>["name"];
  label: string;
  onPress: () => void;
}) {
  const [focused, setFocused] = React.useState(false);
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      onPress={onPress}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={({ pressed }) => ({
        width: 48,
        height: 48,
        borderRadius: 24,
        borderWidth: 3,
        borderColor: focused ? c.ink : "transparent",
        backgroundColor: pressed ? c.rule : c.pale,
        alignItems: "center",
        justifyContent: "center",
      })}
    >
      <Feather name={name} size={22} color={c.ink} />
    </Pressable>
  );
}
