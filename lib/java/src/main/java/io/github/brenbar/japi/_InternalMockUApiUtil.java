package io.github.brenbar.japi;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.stream.Collectors;

class _InternalMockUApiUtil {

  public static String getJson() {
    var stream = Thread.currentThread().getContextClassLoader().getResourceAsStream("mock-internal.japi.json");
    return new BufferedReader(new InputStreamReader(stream)).lines().collect(Collectors.joining("\n"));
  };

}
