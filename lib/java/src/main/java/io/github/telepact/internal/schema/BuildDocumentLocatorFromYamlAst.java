//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.schema;

import java.io.StringReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.databind.ObjectMapper;

import org.yaml.snakeyaml.Yaml;
import org.yaml.snakeyaml.error.Mark;
import org.yaml.snakeyaml.nodes.MappingNode;
import org.yaml.snakeyaml.nodes.Node;
import org.yaml.snakeyaml.nodes.NodeTuple;
import org.yaml.snakeyaml.nodes.ScalarNode;
import org.yaml.snakeyaml.nodes.SequenceNode;

import io.github.telepact.internal.schema.DocumentLocators.DocumentLocator;

public class BuildDocumentLocatorFromYamlAst {
    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    public static DocumentLocator createDocumentLocatorFromYamlText(String text) throws Exception {
        final var root = new Yaml().compose(new StringReader(text));
        if (root == null) {
            throw new IllegalArgumentException("YAML document cannot be empty");
        }

        validateNoDuplicateKeys(root);
        final var locations = new HashMap<String, Map<String, Object>>();
        locations.put(serializePath(List.of()), coordinatesFromMark(root.getStartMark()));
        buildLocationsForNode(root, List.of(), locations);

        return path -> new HashMap<>(locations.getOrDefault(serializePath(path), defaultDocumentCoordinates()));
    }

    private static void buildLocationsForNode(
            Node node,
            List<Object> path,
            Map<String, Map<String, Object>> locations) throws Exception {
        if (node instanceof SequenceNode sequenceNode) {
            final var values = sequenceNode.getValue();
            for (int index = 0; index < values.size(); index += 1) {
                final var child = values.get(index);
                final var childPath = new ArrayList<>(path);
                childPath.add(index);
                locations.put(serializePath(childPath), coordinatesFromMark(child.getStartMark()));
                buildLocationsForNode(child, childPath, locations);
            }
            return;
        }

        if (node instanceof MappingNode mappingNode) {
            for (final NodeTuple tuple : mappingNode.getValue()) {
                if (!(tuple.getKeyNode() instanceof ScalarNode keyNode)) {
                    continue;
                }

                final var keyPath = new ArrayList<>(path);
                keyPath.add(keyNode.getValue());
                locations.put(serializePath(keyPath), coordinatesFromMark(keyNode.getStartMark()));
                buildLocationsForNode(tuple.getValueNode(), keyPath, locations);
            }
        }
    }

    private static void validateNoDuplicateKeys(Node node) {
        if (node instanceof SequenceNode sequenceNode) {
            for (final var child : sequenceNode.getValue()) {
                validateNoDuplicateKeys(child);
            }
            return;
        }

        if (node instanceof MappingNode mappingNode) {
            final var seenKeys = new java.util.HashSet<String>();
            for (final NodeTuple tuple : mappingNode.getValue()) {
                final var key = tuple.getKeyNode() instanceof ScalarNode scalarNode
                        ? scalarNode.getValue()
                        : String.valueOf(tuple.getKeyNode());
                if (!seenKeys.add(key)) {
                    throw new IllegalArgumentException("Duplicate YAML key");
                }
                validateNoDuplicateKeys(tuple.getValueNode());
            }
        }
    }

    private static Map<String, Object> coordinatesFromMark(Mark mark) {
        if (mark == null) {
            return defaultDocumentCoordinates();
        }
        return coordinates(mark.getLine() + 1, mark.getColumn() + 1);
    }

    private static Map<String, Object> coordinates(int row, int col) {
        return Map.of("row", row, "col", col);
    }

    private static Map<String, Object> defaultDocumentCoordinates() {
        return coordinates(1, 1);
    }

    private static String serializePath(List<Object> path) {
        try {
            return OBJECT_MAPPER.writeValueAsString(path);
        } catch (Exception e) {
            return "[]";
        }
    }
}
