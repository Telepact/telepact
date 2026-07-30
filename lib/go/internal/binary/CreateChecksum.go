//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package binary

import "hash/crc32"

// CreateChecksum produces a signed 32-bit CRC checksum for the provided string value.
func CreateChecksum(value string) int {
	checksum := crc32.ChecksumIEEE([]byte(value))
	return int(int32(checksum))
}
