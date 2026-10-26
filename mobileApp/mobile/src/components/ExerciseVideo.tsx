
import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { useVideoPlayer, VideoView } from "expo-video";
import { SvgUri } from "react-native-svg";

const videoFiles: Record<string, number> = {
  "sit_to_stand.svg": require("../../assets/exercises/sit_to_stand.mp4"),
};

type Props = {
  image?: string | null;
  name: string;
  apiUrl?: string;
};

function VideoPlayer({ source }: { source: number }) {
  const player = useVideoPlayer(source, (player) => {
    player.loop = true;
  });

  return (
    <VideoView
      player={player}
      style={styles.video}
      nativeControls
      contentFit="contain"
    />
  );
}

export default function ExerciseVideo({
  image,
  name,
  apiUrl = "http://127.0.0.1:8000",
}: Props) {
  const filename = image?.split("/").pop() ?? "";
  const source = videoFiles[filename];

  if (source) {
    return <VideoPlayer source={source} />;
  }

  if (image) {
    const url = image.startsWith("http")
      ? image
      : `${apiUrl}/content/${filename}`;

    return (
      <View style={styles.fallback}>
        <SvgUri
          uri={url}
          width="100%"
          height={220}
        />
      </View>
    );
  }

  return (
    <View style={styles.fallback}>
      <Text accessibilityRole="text">
        {name}: Follow the written exercise instructions.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  video: {
    width: "100%",
    aspectRatio: 16 / 9,
    borderRadius: 16,
    backgroundColor: "#101827",
  },
  fallback: {
    width: "100%",
    minHeight: 220,
    justifyContent: "center",
    alignItems: "center",
  },
});
