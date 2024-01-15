package io.github.brenbar.uapi;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.stream.Collectors;

class _InternalUApiUtil {

  public static String getJson() {
    var stream = Thread.currentThread().getContextClassLoader().getResourceAsStream("internal.japi.json");
    return new BufferedReader(new InputStreamReader(stream)).lines().collect(Collectors.joining("\n"));
  };
}
