
import React, { useEffect, useRef } from "react";
import {
  Animated,
  Easing,
  Pressable,
  ViewStyle,
  Platform,
} from "react-native";

type HoverCardProps = {
  children: React.ReactNode;
  style?: ViewStyle;
  floating?: boolean;
  onPress?: () => void;
};

export default function HoverCard({
  children,
  style,
  floating = false,
  onPress,
}: HoverCardProps) {
  const lift = useRef(new Animated.Value(0)).current;
  const float = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (!floating || Platform.OS !== "web") {
      return;
    }

    const animation = Animated.loop(
      Animated.sequence([
        Animated.timing(float, {
          toValue: 1,
          duration: 2600,
          easing: Easing.inOut(Easing.sin),
          useNativeDriver: true,
        }),
        Animated.timing(float, {
          toValue: 0,
          duration: 2600,
          easing: Easing.inOut(Easing.sin),
          useNativeDriver: true,
        }),
      ]),
    );

    animation.start();

    return () => animation.stop();
  }, [floating, float]);

  const hoverTransform = lift.interpolate({
    inputRange: [0, 1],
    outputRange: [0, -7],
  });

  const floatingTransform = float.interpolate({
    inputRange: [0, 1],
    outputRange: [0, -6],
  });

  const Wrapper = onPress ? Pressable : Animated.View;

  if (onPress) {
    return (
      <Pressable
        onPress={onPress}
        onHoverIn={() => {
          Animated.spring(lift, {
            toValue: 1,
            friction: 7,
            useNativeDriver: true,
          }).start();
        }}
        onHoverOut={() => {
          Animated.spring(lift, {
            toValue: 0,
            friction: 7,
            useNativeDriver: true,
          }).start();
        }}
        style={style}
      >
        <Animated.View
          style={{
            transform: [{ translateY: hoverTransform }],
          }}
        >
          {children}
        </Animated.View>
      </Pressable>
    );
  }

  return (
    <Pressable
      onHoverIn={() => {
        Animated.spring(lift, {
          toValue: 1,
          friction: 7,
          useNativeDriver: true,
        }).start();
      }}
      onHoverOut={() => {
        Animated.spring(lift, {
          toValue: 0,
          friction: 7,
          useNativeDriver: true,
        }).start();
      }}
    >
      <Animated.View
        style={[
          style,
          {
            transform: [
              { translateY: hoverTransform },
              { translateY: floatingTransform },
            ],
          },
        ]}
      >
        {children}
      </Animated.View>
    </Pressable>
  );
}
