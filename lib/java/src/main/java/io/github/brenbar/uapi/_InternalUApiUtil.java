package io.github.brenbar.uapi;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.stream.Collectors;

class _InternalUApiUtil {

  public static String getJson() {
    final var stream = Thread.currentThread().getContextClassLoader().getResourceAsStream("internal.uapi.json");
    return new BufferedReader(new InputStreamReader(stream)).lines().collect(Collectors.joining("\n"));
  };
}
