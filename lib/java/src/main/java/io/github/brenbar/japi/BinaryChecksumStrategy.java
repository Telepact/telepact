package io.github.brenbar.japi;

import java.util.List;

public interface BinaryChecksumStrategy {

    void update(Integer checksum);

    List<Integer> get();

}
