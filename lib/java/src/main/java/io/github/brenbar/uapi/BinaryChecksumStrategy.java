package io.github.brenbar.uapi;

import java.util.List;

public interface BinaryChecksumStrategy {

    void update(Integer checksum);

    List<Integer> get();

}
